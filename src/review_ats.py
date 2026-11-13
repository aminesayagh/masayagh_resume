#!/usr/bin/env python3
"""Review a resume PDF against one job posting in one command (ATS reviewer, milestone 4).

Usage: python3 src/review_ats.py --job jobs/<slug>/job.json [--cv jobs/<slug>/resume.pdf]
                             [--content jobs/<slug>/content/content.json] [--out jobs/<slug>/review/review.md] [--no-network]
       python3 src/review_ats.py --job jobs/<slug>/job.json --preview

--preview prints one line per requirement term (met/partial/missing and the PDF line it
matched) and writes nothing. It accepts unreviewed requirements, so it works while drafting.
It then compares against the last saved review.json: what changed, and any regression
(a term losing status, lower coverage, more pages or findings). Save a new baseline by
running without --preview.

Runs the spelling, style, PDF-text and job-matching checks and writes a readable Markdown
report plus a JSON report next to it, and interview.json: one prep topic per requirement. Human overrides in the job file ("overrides") are
applied, with the automated finding kept visible. This is a tailoring aid: it never
predicts an employer's ATS score or a hiring outcome.
Exit code: 0 = report written, 1 = invalid job file, unreadable PDF, or PDF errors.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from pypdf import PdfReader

import check_job
import paths
import offers
import check_pdf
import db
import check_spelling
import check_style
import match_job

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # repo root: template/, src/, jobs/
COVERAGE_VERSION = 4
COVERAGE_FORMULA = ("Σ weight × (1 met, 0.5 partial, 0 otherwise) ÷ Σ weight, per priority; "
                    "weight by skill type (TYPE_WEIGHTS); overall also weights must-have 1, preferred 0.25")
PRIORITY_WEIGHTS = {"must_have": 1.0, "preferred": 0.25}  # overall: a preferred skill counts a quarter of a must-have
# ponytail: hardcoded on purpose (the user's choice); move to config.json if they ever want to tune them per job
TYPE_WEIGHTS = {"programming_language": 1.5, "technology": 1.5,     # named languages and products: ATS filters match the exact name
                "technical": 1.0, "ai": 1.0, "design": 1.0,       # hard skills: what the resume must prove
                "education": 0.5, "language": 0.5,                 # usually a fact on the resume, rarely tailored
                "soft": 0.25, "location": 0.25,                    # hard to prove in text / a fact, not a skill
                None: 0.5}                                         # not typed yet
DISCLAIMER = ("This is a tailoring aid, not an ATS score: no single number represents how employers' systems rank "
              "resumes. 'Missing' means no supporting text was found in this PDF, not that you lack the skill.")


def rel(path: Path) -> str:
    p = path.resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(path)


def apply_overrides(results: list[dict], overrides: list[dict], pages: list[str]) -> None:
    """Replace the status with the human decision; keep the automated finding; flag stale quotes."""
    page_text = check_pdf.norm(" ".join(pages))
    by_id = {o["id"]: o for o in overrides}
    for r in results:
        o = by_id.get(r["id"])
        if not o:
            continue
        quote = o.get("pdf_quote")
        stale = bool(quote) and check_pdf.norm(quote) not in page_text
        r["automated"] = {k: r[k] for k in ("status", "quote", "page", "rationale")}
        r["override"] = {"status": o["status"], "reason": o["reason"], "pdf_quote": quote, "stale": stale}
        r["status"] = o["status"]


def suggestion(r: dict) -> str | None:
    """Rule-based edit suggestion: what the posting says vs what the PDF says. Never model-written."""
    if r.get("kind_years"):
        if r["status"] == "partial":
            return ("Your years only reach the minimum if overlapping jobs are added together. Make sure dates are "
                    "clear ranges, and state your total experience in the summary if it is accurate.")
        return None
    hints = []
    for t in r["terms"]:
        if t["keyword"] == "alias":
            hints.append(f"The posting says '{t['term']}'; your PDF says '{t['quote'].strip()}' (p{t['page']}). "
                         f"Use '{t['term']}' if it describes the same thing.")
        elif t["status"] == "partial":
            hints.append(f"'{t['term']}' is only in your {t['section'] if t['section'] != 'skills' else 'skills list'}. "
                         f"If you used it in a job, name it in that job's bullet.")
        elif t["status"] == "missing":
            hints.append(f"'{t['term']}' does not appear. If you truthfully have it, add it in the posting's words; "
                         "if not, leave it out.")
    return " ".join(hints) or None


def coverage(results: list[dict], priority: str | None = None) -> float | None:
    """Weighted by skill type: a soft skill counts less than a hard one. Equal types give (met + 0.5 × partial) ÷ n.
    priority None = overall: every requirement, a preferred one weighted PRIORITY_WEIGHTS lower."""
    rs = [r for r in results if priority in (None, r["priority"])]
    if not rs:
        return None
    weight = lambda r: TYPE_WEIGHTS.get(r.get("type"), TYPE_WEIGHTS[None]) * PRIORITY_WEIGHTS[r["priority"]]
    score = lambda r: 1 if r["status"] == "met" else 0.5 if r["status"] == "partial" else 0
    return round(sum(weight(r) * score(r) for r in rs) / sum(weight(r) for r in rs), 2)


_r = lambda p, s: {"priority": p, "status": s, "type": "technical"}
assert coverage([_r("must_have", "met"), _r("preferred", "missing")]) == 0.8  # 1 ÷ (1 + 0.25)

SENIORITY = {"senior", "sr", "junior", "jr", "lead", "principal", "staff", "mid", "level", "i", "ii", "iii"}
SAME_ROLE = {"developer": "engineer", "dev": "engineer", "programmer": "engineer"}  # ponytail: extend when a real title needs it


def title_core(title: str) -> set[str]:
    """'Senior Front-End Developer' -> {'front', 'end', 'engineer'}: seniority dropped, developer = engineer."""
    words = re.findall(r"[a-z0-9]+", title.casefold())
    return {SAME_ROLE.get(w, w) for w in words if w not in SENIORITY}


def title_check(job: dict, content: dict | None) -> dict | None:
    """Recruiters and ATS searches match the job title first: warn when the resume's role is a different
    role. Seniority and developer/engineer wording may differ; the role itself (front-end, data...) may not."""
    if " — " not in job["title"]:  # job titles are "Company — Title"; the template baseline has none
        return None
    posting = job["title"].split(" — ", 1)[1].strip()
    resume = (content or {}).get("role", "")
    same = bool(title_core(posting)) and title_core(posting) == title_core(resume)
    return {"posting": posting, "resume": resume, "match": same, "severity": "ok" if same else "warning",
            "message": f"Resume title '{resume}' matches the posting's '{posting}' (seniority and developer/engineer wording aside)."
            if same else
            f"Resume title '{resume}' differs from the posting's title '{posting}'. Recruiters and ATS searches "
            f"match on the title first; use a title for the same role in content.json's 'role' if it truthfully describes you."}


def review(job: dict, pdf: Path, content: dict | None, network: bool, letter: Path | None = None, con=None) -> dict:
    """letter: the English cover letter PDF, searched as a claim (partial), like the skills list."""
    headings = check_pdf.template_headings(check_pdf.TEMPLATE)
    pdf_report = check_pdf.check(pdf, content, headings, network=network)
    pages = [p.extract_text() or "" for p in PdfReader(pdf).pages] if pdf_report["pages"] else []
    aliases = db.aliases(con)  # skills + keywords in data/resume.db (was src/aliases.json)
    letter_pages = [p.extract_text() or "" for p in PdfReader(letter).pages] if letter and letter.exists() else []
    match = match_job.assess(job, pages, content, headings, aliases, letter_pages)
    reqs = {r["id"]: r for r in job["requirements"]}
    for r in match["results"]:
        r["kind_years"] = reqs[r["id"]].get("kind") == "years_experience"
        r["type"] = reqs[r["id"]].get("type")  # the skill's type, for the weighted coverage
    apply_overrides(match["results"], job.get("overrides", []), pages)
    for r in match["results"]:
        r["suggestion"] = suggestion(r) if r["status"] != "met" or any(t["keyword"] == "alias" for t in r["terms"]) else None
    results = match["results"]
    counts = {s: sum(r["status"] == s for r in results) for s in ("met", "partial", "missing", "uncertain")}
    return {
        "title": job["title"], "generated": date.today().isoformat(), "disclaimer": DISCLAIMER,
        "unreviewed": sum(not r.get("reviewed") for r in job["requirements"]),
        "job_title": title_check(job, content),
        "pdf_check": pdf_report,
        "spelling": check_spelling.check(content, headings, check_spelling.load_allow()) if content else None,
        "style": check_style.check(content) if content else None,
        "match_version": match["version"], "results": results, "counts": counts,
        "overridden": sum("override" in r for r in results),
        "evidence_coverage": {"version": COVERAGE_VERSION, "formula": COVERAGE_FORMULA,
                              "must_have": coverage(results, "must_have"), "preferred": coverage(results, "preferred"),
                              "overall": coverage(results)},
    }


def placement_gaps(rep: dict) -> list[dict]:
    """Terms missing from a resume section the offer targets (its requirements' "targets")."""
    return [{"id": r["id"], "priority": r["priority"], "term": t["term"], "targets": r["targets"],
             "found_in": t["found_in"], "missing_from": t["missing_from"]}
            for r in rep["results"] if r.get("targets") for t in r.get("terms", []) if t.get("missing_from")]


def md_requirement(r: dict) -> list[str]:
    out = [f"#### {r['id']} · {r['status']} · {r['description']}", "",
           f"- **Posting:** \"{r['posting_quote']}\""]
    if r["quote"]:
        out.append(f"- **Your PDF** (page {r['page']}): \"{r['quote']}\"")
    out.append(f"- **Keyword:** {r['keyword']}" if r["keyword"] else "- **Keyword:** computed from job dates")
    out.append(f"- **Why:** {r['rationale']}")
    if r.get("override"):
        o = r["override"]
        out.append(f"- **Your decision:** {o['status']} ({o['reason']}). Automated finding: {r['automated']['status']}."
                   + (" ⚠️ **Stale:** the PDF text this decision relied on is no longer in the PDF; review it again."
                      if o["stale"] else ""))
    if r["suggestion"]:
        out.append(f"- **Suggestion:** {r['suggestion']}")
    return out + [""]


def markdown(rep: dict, inputs: dict) -> str:
    results, pdf = rep["results"], rep["pdf_check"]
    by = lambda sev: [f for f in pdf["findings"] if f["severity"] == sev]
    must = [r for r in results if r["priority"] == "must_have"]
    pref = [r for r in results if r["priority"] == "preferred"]
    L = [f"# ATS review: {rep['title']}", "",
         f"Generated {rep['generated']} from `{inputs['cv']}`, `{inputs['job']}` and `{inputs['content']}`.", "",
         f"> {rep['disclaimer']}", ""]
    if rep.get("unreviewed"):
        L += [f"**Draft:** {rep['unreviewed']} requirement(s) not reviewed yet; quotes and priorities may change.", ""]
    if rep.get("job_title") and not rep["job_title"]["match"]:
        L += [f"**Warning, job title:** {rep['job_title']['message']}", ""]

    gaps = placement_gaps(rep)
    if gaps:
        L += ["## Placement gaps", "", "Terms the job file targets for a resume section where they are not yet found.", "",
              "| Req | Term | Wanted in | Found in | Missing from |", "|---|---|---|---|---|"]
        L += [f"| {g['id']} | {g['term']} | {', '.join(g['targets'])} | {', '.join(g['found_in']) or '-'} | "
              f"{', '.join(g['missing_from'])} |" for g in gaps]
        L.append("")
    decisions = [f"- **{r['id']}** must-have is **{r['status']}**: {r['description']}" for r in must if r["status"] != "met"]
    decisions += [f"- **{r['id']}** override is **stale**: re-check it against the current PDF" for r in results
                  if r.get("override", {}).get("stale")]
    decisions += [f"- PDF error: {f['message']}" for f in by("error")]
    L += ["## Decisions for you", ""] + (decisions or ["- Nothing blocking. Review the suggestions below."]) + [""]

    L += ["## 1. PDF readability", "",
          f"{len(pdf['pages'])} page(s): {len(by('error'))} error(s), {len(by('warning'))} warning(s), {len(by('info'))} note(s).", ""]
    L += [f"- **{f['severity']}**: {f['message']}" for f in by("error") + by("warning") + by("info")] + [""]

    L += ["## 2. Content checks", ""]
    for name in ("spelling", "style"):
        found = (rep[name] or {}).get("findings", [])
        L += [f"**{name.capitalize()}:** {sum(f['severity'] == 'warning' for f in found)} warning(s).", ""]
        L += [f"- {f['message']}" for f in found] + [""]

    for title, group in (("3. Must-have requirements", must), ("4. Preferred requirements", pref)):
        L += [f"## {title}", ""]
        for status in ("missing", "uncertain", "partial", "met"):  # gaps first
            L += [line for r in group if r["status"] == status for line in md_requirement(r)]

    c, cov = rep["counts"], rep["evidence_coverage"]
    pct = lambda v: "n/a" if v is None else f"{round(v * 100)}%"
    L += ["## Summary", "",
          "| | met | partial | missing | uncertain |", "|---|---|---|---|---|",
          *[f"| {label} | " + " | ".join(str(sum(r['status'] == s for r in g)) for s in ("met", "partial", "missing", "uncertain")) + " |"
            for label, g in (("Must-have", must), ("Preferred", pref))], "",
          f"{rep['overridden']} result(s) set by your overrides.", "",
          f"**Evidence coverage** (v{cov['version']}): overall {pct(cov.get('overall'))}, must-have {pct(cov['must_have'])}, "
          f"preferred {pct(cov['preferred'])}. "
          f"Formula: {cov['formula']}. It measures how much of this posting your PDF text backs up. It is not a hiring "
          "probability or an ATS score, and it is kept separate from PDF readability on purpose.", ""]
    return "\n".join(L)


def print_preview(rep: dict) -> None:
    for r in rep["results"]:
        print(f"{r['id']} {r['priority']:<9} {r['status']:<9} {r.get('description', '')}")
        for t in r.get("terms", []):
            quote = f'  "{t["quote"][:70]}"' if t.get("quote") else ""
            print(f"    {t['term']}: {t['status']} ({t['keyword']}){quote}")
    for g in placement_gaps(rep):
        print(f"  placement: {g['id']} {g['term']} missing from {', '.join(g['missing_from'])} "
              f"(found in {', '.join(g['found_in']) or 'nothing'})")
    spelling = len(rep["spelling"]["findings"])
    pdf = sum(f["severity"] != "info" for f in rep["pdf_check"]["findings"])
    cov = rep["evidence_coverage"]
    if rep.get("job_title") and not rep["job_title"]["match"]:
        print(f"\n[warning] {rep['job_title']['message']}")
    print(f"\nPreview, nothing written. Spelling warnings: {spelling}. PDF errors/warnings: {pdf}.")
    print(f"Evidence coverage v{cov['version']}: overall {cov.get('overall')}, must-have {cov['must_have']}, preferred {cov['preferred']} "
          f"= {cov['formula']} (not an ATS score)")


FOCUS = {"met": "prepare_story", "partial": "prove_claim", "uncertain": "prove_claim", "missing": "gap"}
HOW_TO_PREPARE = {
    "source": "General interview-prep guidance (STAR: situation, task, action, result), the same for every job. "
              "Only 'topics' comes from this posting and this resume.",
    "prepare_story": "Interviewers ask about what's written. Prepare the story behind the line: the situation, "
                     "what you built, your choices, the result, and what you'd do differently.",
    "prove_claim": "Your resume only claims this (skills, summary, or some of the terms). Prepare one concrete "
                   "example that turns the claim into proof: scope, your role, a decision, the result.",
    "gap": "Not on your resume. Prepare an honest answer: related experience, or how you would learn it.",
}


def interview(rep: dict, job: dict) -> dict:
    """Prep sheet: the review's facts per requirement, most important first. No generated advice."""
    posting = {q["id"]: q.get("quote", "") for q in job.get("requirements", [])}
    order = {"prove_claim": 0, "prepare_story": 1, "gap": 2}
    topics = [{"id": r["id"], "priority": r["priority"], "focus": FOCUS[r["status"]],
               "requirement": r.get("description", ""), "posting_says": posting.get(r["id"], ""),
               "your_resume_says": list(dict.fromkeys(t["quote"] for t in r.get("terms", []) if t.get("quote"))),
               "terms_not_met": [t["term"] for t in r.get("terms", []) if t["status"] != "met"]}
              for r in rep["results"]]
    topics.sort(key=lambda t: (t["priority"] != "must_have", order[t["focus"]]))
    return {"job": rep["title"], "generated": rep["generated"], "draft_requirements_unreviewed": rep.get("unreviewed", 0),
            "summary": {f: sum(t["focus"] == f for t in topics) for f in order},
            "how_to_prepare": HOW_TO_PREPARE, "topics": topics}


RANK = {"missing": 0, "uncertain": 0, "partial": 1, "met": 2}


def summary(rep: dict) -> dict:
    """The numbers compared between a saved report and a preview."""
    return {"terms": {(r["id"], t["term"]): t["status"] for r in rep["results"] for t in r.get("terms", [])},
            "must_have": rep["evidence_coverage"]["must_have"], "preferred": rep["evidence_coverage"]["preferred"],
            "overall": rep["evidence_coverage"].get("overall"),
            "pages": len(rep["pdf_check"]["pages"]), "spelling": len(rep["spelling"]["findings"]),
            "pdf": sum(f["severity"] != "info" for f in rep["pdf_check"]["findings"]),
            "style": sum(f["severity"] == "warning" for f in (rep.get("style") or {}).get("findings", [])),
            "title_mismatch": int(bool(rep.get("job_title") and not rep["job_title"]["match"]))}


def compare(old: dict, new: dict) -> tuple[list[str], list[str]]:
    """(changes, regressions) between two summary() results."""
    changes, regressions = [], []
    for key, status in new["terms"].items():
        before = old["terms"].get(key)
        if before is not None and before != status:
            line = f"{key[0]} {key[1]}: {before} → {status}"
            changes.append(line)
            if RANK[status] < RANK[before]:
                regressions.append(line)
    for k in ("overall", "must_have", "preferred"):
        if (old.get(k) or 0) != (new.get(k) or 0):
            changes.append(f"{k} coverage {old.get(k)} → {new.get(k)}")
            if (new.get(k) or 0) < (old.get(k) or 0):
                regressions.append(f"{k} coverage {old.get(k)} → {new.get(k)}")
    for k in ("pages", "spelling", "style", "pdf", "title_mismatch"):
        if old.get(k, 0) != new.get(k, 0):
            changes.append(f"{k} {old.get(k, 0)} → {new.get(k, 0)}")
            if new.get(k, 0) > old.get(k, 0):
                regressions.append(f"{k} {old.get(k, 0)} → {new.get(k, 0)}")
    return changes, regressions


def refresh(job_path: Path, job: dict, cv: Path, content_path: Path, network: bool = False,
            md_path: Path | None = None) -> dict:
    """Review the PDF, print what changed since the last saved report (and the verdict), then save the
    report and interview.json. Runs after every job PDF build, so the dashboard app never shows a stale review."""
    content = json.loads(content_path.read_text(encoding="utf-8")) if content_path.exists() else None
    md_path = md_path or paths.review_md(job_path.parent)
    previous = md_path.with_suffix(".json")
    letter = paths.cover_pdf(job_path.parent)  # ponytail: a resume build reviews before its letter is rebuilt, so a
    letter = letter if letter.exists() else paths.not_ready(letter)  # changed letter counts from the next review
    rep = review(job, cv, content, network=network, letter=letter)
    if previous.exists():
        changes, regressions = compare(summary(json.loads(previous.read_text(encoding="utf-8"))), summary(rep))
        print(f"Compared with the previous report:")
        print("\n".join(f"  {c}" for c in changes) or "  no change")
        print(f"Verdict: {'REGRESSION: ' + '; '.join(regressions) if regressions else 'no regression'}")
    inputs = {"cv": rel(cv), "job": rel(job_path), "content": rel(content_path) if content else "no content file"}
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown(rep, inputs), encoding="utf-8")
    rep["pdf_check"]["pdf"] = inputs["cv"]
    previous.write_text(json.dumps({**inputs, **rep}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    interview_path = md_path.parent / "interview.json"
    interview_path.write_text(json.dumps(interview(rep, job), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    c, cov = rep["counts"], rep["evidence_coverage"]
    errors = sum(f["severity"] == "error" for f in rep["pdf_check"]["findings"])
    print(f"{rep['title']}\n  PDF: {errors} error(s), "
          f"{sum(f['severity'] == 'warning' for f in rep['pdf_check']['findings'])} warning(s)")
    if rep.get("unreviewed"):
        print(f"  Draft: {rep['unreviewed']} requirement(s) not reviewed yet; quotes and priorities may change.")
    if rep.get("job_title") and not rep["job_title"]["match"]:
        print(f"  [warning] {rep['job_title']['message']}")
    print(f"  Requirements: {c['met']} met, {c['partial']} partial, {c['missing']} missing, {c['uncertain']} uncertain "
          f"({rep['overridden']} overridden)")
    print(f"  Evidence coverage v{cov['version']}: overall {cov.get('overall')}, must-have {cov['must_have']}, "
          f"preferred {cov['preferred']} (not an ATS score)")
    print(f"  Report: {rel(md_path)} (+ .json); interview prep: {rel(interview_path)}")
    print(f"  Dashboard: http://127.0.0.1:8765/job/{job_path.parent.name} (run the dashboard app)")
    return rep


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--job", type=Path, required=True, help="jobs/<slug> (or jobs/<slug>/job.json)")
    parser.add_argument("--cv", type=Path, help="resume PDF (default: the job's pdf/<pdf_name>)")
    parser.add_argument("--content", type=Path, help="content JSON (default: the job's content/content.json)")
    parser.add_argument("--out", type=Path, help="Markdown report (default: the job's review/review.md); JSON is saved beside it")
    parser.add_argument("--no-network", action="store_true", help="skip opening the links in the PDF")
    parser.add_argument("--preview", action="store_true",
                        help="print the match per requirement and write no report; unreviewed requirements allowed")
    args = parser.parse_args()

    args.job = paths.job(paths.folder_arg(args.job))
    job = offers.load(args.job.parent)
    # Unreviewed requirements are allowed; the report is then labelled draft everywhere.
    problems = [f for f in check_job.validate(job, draft=True) if f["severity"] == "error"
                and f["code"] != "requirements"]  # a posting that asks for nothing still gets PDF, spelling and style
    if problems:
        print(f"The job file is not valid; fix it first (python3 src/check_job.py {args.job}):")
        for f in problems:
            print(f"  [error] {f['message']}")
        sys.exit(1)
    folder = args.job.parent
    cv = args.cv or paths.resume_pdf(folder)
    if not cv.exists() and paths.not_ready(cv).exists():  # not ready to send (see build_resume.mark_readiness)
        cv = paths.not_ready(cv)
    content_path = args.content or paths.content(folder)
    content = json.loads(content_path.read_text(encoding="utf-8")) if content_path.exists() else None

    if args.preview:
        letter = paths.cover_pdf(folder)  # the employer gets it inside the combined PDF: its words count as claims
        rep = review(job, cv, content, network=False, letter=letter if letter.exists() else paths.not_ready(letter))
        print_preview(rep)
        saved = paths.review_json(args.job.parent)
        if not saved.exists():
            print("No saved review.json to compare with; run without --preview to save a baseline.")
            return
        changes, regressions = compare(summary(json.loads(saved.read_text(encoding="utf-8"))), summary(rep))
        print(f"\nCompared with {rel(saved)}:")
        print("\n".join(f"  {c}" for c in changes) or "  no change")
        print(f"Verdict: {'REGRESSION: ' + '; '.join(regressions) if regressions else 'no regression'}")
        return
    rep = refresh(args.job, job, cv, content_path, network=not args.no_network, md_path=args.out)
    errors = sum(f["severity"] == "error" for f in rep["pdf_check"]["findings"])
    sys.exit(1 if errors or not rep["pdf_check"]["pages"] else 0)


if __name__ == "__main__":
    main()
