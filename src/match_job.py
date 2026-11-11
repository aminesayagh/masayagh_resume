#!/usr/bin/env python3
"""Match a reviewed job file against the resume PDF text (ATS reviewer, milestone 3).

Usage: python3 src/match_job.py jobs/<slug>/job.json [--cv jobs/<slug>/resume.pdf] [--content jobs/<slug>/content.json]

For each requirement it reports two separate things:
  keyword   - does the posting's exact term appear anywhere in the PDF (what recruiter search sees):
              exact | alias (wording differs) | absent
  evidence  - does the resume back it up:
              met       found in experience, education, languages or header text
              partial   found only in the skills list or summary (a claim, not proof),
                        or only some of the requirement's terms are met
              missing   no supporting text in this PDF (not proof you lack the skill)
              uncertain the text cannot support a decision (e.g. unreadable dates)
Every met/partial result cites an exact PDF line and page. Deterministic: no model, no network.
Exit code: 0 = report written, 1 = invalid job file or unreadable PDF.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

import check_job
import check_pdf
import paths
import offers
import db

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # repo root: template/, src/, jobs/
VERSION = 2  # 2: Languages heading found, Projects and Certifications count as evidence. Bump when matching rules change, so old reports can be told apart
EVIDENCE_SECTIONS = {"experience", "projects", "certifications", "education", "languages", "header"}
CLAIM_SECTIONS = {"skills", "summary"}
SECTION_WORDS = [("summary", "summary"), ("skills", "skill"), ("skills", "proficienc"), ("education", "education"),
                 ("languages", "language"), ("experience", "experience"), ("projects", "project"),
                 ("certifications", "certific")]  # first match wins: "Summary of Experience" is summary


def section_kind(heading: str) -> str:
    h = check_pdf.norm(heading)
    return next(kind for kind, word in SECTION_WORDS + [("other", "")] if word in h)


def pdf_lines(pages: list[str], headings: list[str]) -> list[dict]:
    """Every non-empty PDF line with its page and the resume section it sits in."""
    heads = {check_pdf.norm(h): section_kind(h) for h in headings}
    edges = [[l for l in t.splitlines() if l.strip()] for t in pages]
    footer = None
    if len(pages) > 1 and len({re.sub(r"\d+", "#", check_pdf.norm(e[-1])) for e in edges if e}) == 1:
        footer = re.sub(r"\d+", "#", check_pdf.norm(edges[0][-1]))
    out, section = [], "header"
    for page, lines in enumerate(edges, 1):
        i = 0
        while i < len(lines):
            line, n = lines[i], check_pdf.norm(lines[i])
            pair = check_pdf.norm(line + " " + lines[i + 1]) if i + 1 < len(lines) else None
            if n in heads:
                section = heads[n]
            elif pair in heads:
                section, i = heads[pair], i + 1
            elif footer and re.sub(r"\d+", "#", n) == footer:
                out.append({"page": page, "section": "footer", "text": line})
            else:
                inline = next((h for h in heads if n.startswith(h + " ")), None)  # "Languages Arabic - Native ..."
                if inline:
                    section = heads[inline]
                out.append({"page": page, "section": section, "text": line})
            i += 1
    return out


def term_pattern(term: str) -> re.Pattern:
    body = re.escape(term).replace(r"\ ", r"\s+").replace(r"\-", r"[-\s]")
    return re.compile(rf"(?<![\w/.]){body}(?:e?s)?(?![\w])", re.I)  # optional plural; "SQL" never matches "PostgreSQL"


def find_term(term: str, lines: list[dict]) -> list[dict]:
    """Lines (or two consecutive lines on one page, for a term split by a line break) containing the term."""
    pat, hits = term_pattern(term), []
    for i, line in enumerate(lines):
        if pat.search(line["text"]):
            hits.append({**line, "quote": line["text"]})
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if nxt and nxt["page"] == line["page"] and nxt["section"] == line["section"]:
            joined = line["text"] + " " + nxt["text"]
            m = pat.search(joined)
            if m and m.start() < len(line["text"]) < m.end():
                hits.append({**line, "quote": joined})
    return hits


def match_term(term: str, lines: list[dict], aliases: dict) -> dict:
    exact = find_term(term, lines)
    alias_hits = []
    if not exact:
        for alias in aliases.get(term.casefold(), []):
            alias_hits += [{**h, "alias": alias} for h in find_term(alias, lines)]
    hits = exact or alias_hits
    keyword = "exact" if exact else "alias" if alias_hits else "absent"
    evidence = [h for h in hits if h["section"] in EVIDENCE_SECTIONS]
    claims = [h for h in hits if h["section"] in CLAIM_SECTIONS]
    best = (evidence or claims or [None])[0]
    status = "met" if evidence else "partial" if claims else "missing"
    label = {"skills": "skills list", "summary": "summary"}
    where = {"met": f"{best['section']} text" if best else "",
             "partial": f"the {label.get(best['section'], best['section'])} only" if best else "", "missing": ""}[status]
    rationale = (f"'{term}' found in {where}." if status != "missing" else f"'{term}' not found in this PDF.")
    if keyword == "alias":
        rationale += f" Wording differs: the PDF says '{best['alias']}'; the posting says '{term}'. Use the posting's term."
    if status == "partial":
        rationale += " A skills-list or summary mention is a claim, not proof of professional experience."
    return {"term": term, "keyword": keyword, "status": status, "method": "exact" if exact else "alias" if alias_hits else None,
            "quote": best["quote"] if best else None, "page": best["page"] if best else None,
            "section": best["section"] if best else None, "rationale": rationale,
            "found_in": sorted({h["section"] for h in hits})}


def summarize(terms: list[dict]) -> str:
    """One line for a multi-term requirement; per-term detail stays in the report's 'terms'."""
    group = lambda status: ", ".join(t["term"] for t in terms if t["status"] == status)
    parts = [f"{label}: {group(s)}." for s, label in (("met", "Backed by experience"),
             ("partial", "Skills list or summary only"), ("missing", "Not found")) if group(s)]
    differs = [f"'{t['term']}' (PDF: '{t['quote']}')" for t in terms if t["keyword"] == "alias"]
    if differs:
        parts.append("Wording differs for " + ", ".join(differs) + "; use the posting's term.")
    return " ".join(parts)


def match_years(req: dict, content: dict, lines: list[dict]) -> dict:
    notes = []
    years = check_pdf.check_dates(content, lambda sev, code, msg, **kw: notes.append((sev, code)))
    need = req["min_years"]
    if not years or any(code in {"date_format", "date_order"} for _, code in notes):
        return {"status": "uncertain", "method": "computed", "quote": None, "page": None,
                "rationale": "Some job dates could not be read, so years of experience cannot be computed reliably."}
    starts = [j["dates"] for j in content.get("experience", [])]
    earliest = min(starts, key=lambda d: check_pdf.parse_month(re.split(r"\s*[-–—]\s*", d)[0], False) or 10**9)
    start = re.split(r"\s*[-\u2013\u2014]\s*", earliest)[0]  # the template may print start and end on separate lines
    hit = next((h for h in find_term(earliest, lines) or find_term(start, lines)), None)
    if years["merged"] >= need:
        status, why = "met", f"{years['merged']} years with overlaps counted once (needs {need})."
    elif years["summed"] >= need:
        status, why = "partial", (f"{years['merged']} years with overlaps counted once, {years['summed']} if every job "
                                  f"is added (needs {need}); depends on how the parser counts overlaps.")
    else:
        status, why = "missing", f"{years['merged']} years from your dates (needs {need})."
    return {"status": status, "method": "computed", "quote": hit["quote"] if hit else None,
            "page": hit["page"] if hit else None, "years": years,
            "rationale": why + " Computed from the job dates; the quote is your earliest date range."}


def assess(job: dict, pages: list[str], content: dict | None, headings: list[str], aliases: dict) -> dict:
    lines = pdf_lines(pages, headings)
    aliases = {k.casefold(): v for k, v in aliases.items() if not k.startswith("_")}
    results = []
    for req in job["requirements"]:
        base = {k: req.get(k) for k in ("id", "section", "priority", "description", "quote")}
        base["posting_quote"] = base.pop("quote")
        if req.get("kind") == "years_experience":
            r = (match_years(req, content, lines) if content else
                 {"status": "uncertain", "method": "computed", "quote": None, "page": None,
                  "rationale": "No content file, so job dates are unavailable."})
            results.append({**base, "keyword": None, **r, "terms": []})
            continue
        terms = [match_term(t, lines, aliases) for t in req["terms"]]
        for t in terms:  # where the job file wants this term on the resume vs where it is
            t["missing_from"] = [x for x in req.get("targets", []) if x not in t["found_in"]]
        base["targets"] = req.get("targets")
        statuses = {t["status"] for t in terms}
        status = ("met" if statuses == {"met"} else "missing" if statuses == {"missing"} else "partial")
        keyword = ("exact" if all(t["keyword"] == "exact" for t in terms) else
                   "absent" if all(t["keyword"] == "absent" for t in terms) else "alias" if
                   all(t["keyword"] != "absent" for t in terms) else "some")
        best = next((t for t in terms if t["status"] == status), terms[0])
        rationale = best["rationale"] if len(terms) == 1 else summarize(terms)
        results.append({**base, "keyword": keyword, "status": status, "method": best["method"],
                        "quote": best["quote"] if status != "missing" else None,
                        "page": best["page"] if status != "missing" else None, "rationale": rationale, "terms": terms})
    counts = {s: sum(r["status"] == s for r in results) for s in ("met", "partial", "missing", "uncertain")}
    return {"version": VERSION, "counts": counts, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("job", type=Path)
    parser.add_argument("--cv", type=Path, help="resume PDF (default: resume.pdf next to the job file)")
    parser.add_argument("--content", type=Path, help="content JSON (default: content.json or default.json next to the PDF)")
    parser.add_argument("--out", type=Path, help="JSON report path (default: match.json next to the job file)")
    args = parser.parse_args()

    job = offers.read(args.job)
    problems = [f for f in check_job.validate(job) if f["severity"] == "error"]
    if problems:
        print("The job file is not valid; fix it first (python3 src/check_job.py " + str(args.job) + "):")
        for f in problems:
            print(f"  [error] {f['message']}")
        sys.exit(1)
    cv = args.cv or paths.resume_pdf(paths.folder_arg(args.job))
    try:
        pages = [p.extract_text() or "" for p in PdfReader(cv).pages]
    except Exception as exc:
        print(f"[error] PDF could not be read: {exc}")
        sys.exit(1)
    content_path = args.content or (paths.content(folder) if (folder := paths.job_folder(cv))
                                          else ROOT / "template" / "content" / "default.json")
    content = json.loads(content_path.read_text(encoding="utf-8")) if content_path.exists() else None
    aliases = db.aliases()  # skills + keywords in data/resume.db (was src/aliases.json)

    report = assess(job, pages, content, check_pdf.template_headings(check_pdf.TEMPLATE), aliases)
    rel = lambda p: str(p.resolve().relative_to(ROOT)) if p.resolve().is_relative_to(ROOT) else str(p)
    report = {"job": rel(args.job), "cv": rel(cv), "content": rel(content_path) if content else None, **report}
    out = args.out or paths.folder_arg(args.job) / "review" / "match.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for priority in ("must_have", "preferred"):
        print(f"\n{priority.replace('_', '-')}:")
        for r in (r for r in report["results"] if r["priority"] == priority):
            kw = f"keyword {r['keyword']}" if r["keyword"] else "computed"
            print(f"  {r['id']} [{r['status']:9}] {r['description']}  ({kw})")
            if r["quote"]:
                print(f"       p{r['page']}: \"{r['quote']}\"")
            if r["status"] != "met" or r["keyword"] in ("alias", "some"):
                print(f"       {r['rationale']}")
    c = report["counts"]
    print(f"\n{c['met']} met, {c['partial']} partial, {c['missing']} missing, {c['uncertain']} uncertain. Report: {out}")
    print("'missing' means no supporting text in this PDF, not that you lack the skill. Not an ATS score.")


if __name__ == "__main__":
    main()
