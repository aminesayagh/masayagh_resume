#!/usr/bin/env python3
"""Review a resume PDF against one job posting in one command (ATS reviewer, milestone 4).

Usage: python3 src/review_ats.py --job jobs/<slug>/job.json [--cv jobs/<slug>/resume.pdf]
                             [--content jobs/<slug>/content.json] [--out jobs/<slug>/review.md] [--no-network]

Runs the spelling, style, PDF-text and job-matching checks and writes a readable Markdown
report plus a JSON report next to it. Human overrides in the job file ("overrides") are
applied, with the automated finding kept visible. This is a tailoring aid: it never
predicts an employer's ATS score or a hiring outcome.
Exit code: 0 = report written, 1 = invalid job file, unreadable PDF, or PDF errors.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from pypdf import PdfReader

import check_job
import check_pdf
import check_spelling
import check_style
import match_job

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # repo root: template/, src/, jobs/
COVERAGE_VERSION = 1
COVERAGE_FORMULA = "(met + 0.5 × partial) ÷ requirements, per priority; uncertain and missing count 0"
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


def coverage(results: list[dict], priority: str) -> float | None:
    rs = [r for r in results if r["priority"] == priority]
    if not rs:
        return None
    return round((sum(r["status"] == "met" for r in rs) + 0.5 * sum(r["status"] == "partial" for r in rs)) / len(rs), 2)


def review(job: dict, pdf: Path, content: dict | None, network: bool) -> dict:
    headings = check_pdf.template_headings(check_pdf.TEMPLATE)
    pdf_report = check_pdf.check(pdf, content, headings, network=network)
    pages = [p.extract_text() or "" for p in PdfReader(pdf).pages] if pdf_report["pages"] else []
    aliases = json.loads((HERE / "aliases.json").read_text(encoding="utf-8"))
    match = match_job.assess(job, pages, content, headings, aliases)
    reqs = {r["id"]: r for r in job["requirements"]}
    for r in match["results"]:
        r["kind_years"] = reqs[r["id"]].get("kind") == "years_experience"
    apply_overrides(match["results"], job.get("overrides", []), pages)
    for r in match["results"]:
        r["suggestion"] = suggestion(r) if r["status"] != "met" or any(t["keyword"] == "alias" for t in r["terms"]) else None
    results = match["results"]
    counts = {s: sum(r["status"] == s for r in results) for s in ("met", "partial", "missing", "uncertain")}
    return {
        "title": job["title"], "generated": date.today().isoformat(), "disclaimer": DISCLAIMER,
        "pdf_check": pdf_report,
        "spelling": check_spelling.check(content, headings, check_spelling.load_allow()) if content else None,
        "style": check_style.check(content) if content else None,
        "match_version": match["version"], "results": results, "counts": counts,
        "overridden": sum("override" in r for r in results),
        "evidence_coverage": {"version": COVERAGE_VERSION, "formula": COVERAGE_FORMULA,
                              "must_have": coverage(results, "must_have"), "preferred": coverage(results, "preferred")},
    }


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
          f"**Evidence coverage** (v{cov['version']}): must-have {pct(cov['must_have'])}, preferred {pct(cov['preferred'])}. "
          f"Formula: {cov['formula']}. It measures how much of this posting your PDF text backs up. It is not a hiring "
          "probability or an ATS score, and it is kept separate from PDF readability on purpose.", ""]
    return "\n".join(L)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--cv", type=Path, help="resume PDF (default: the job file's pdf_name, else resume.pdf, next to it)")
    parser.add_argument("--content", type=Path, help="content JSON (default: content.json or default.json next to the PDF)")
    parser.add_argument("--out", type=Path, help="Markdown report (default: review.md next to the job file); JSON is saved beside it")
    parser.add_argument("--no-network", action="store_true", help="skip opening the LinkedIn/GitHub/website links")
    args = parser.parse_args()

    job = json.loads(args.job.read_text(encoding="utf-8"))
    problems = [f for f in check_job.validate(job) if f["severity"] == "error"]
    if problems:
        print(f"The job file is not valid; fix it first (python3 src/check_job.py {args.job}):")
        for f in problems:
            print(f"  [error] {f['message']}")
        sys.exit(1)
    cv = args.cv or args.job.parent / job.get("pdf_name", "resume.pdf")
    content_path = args.content or next((p for p in (cv.parent / "content.json", cv.parent / "default.json")
                                          if p.exists()), cv.parent / "content.json")
    content = json.loads(content_path.read_text(encoding="utf-8")) if content_path.exists() else None

    rep = review(job, cv, content, network=not args.no_network)
    inputs = {"cv": rel(cv), "job": rel(args.job), "content": rel(content_path) if content else "no content file"}
    md_path = args.out or args.job.parent / "review.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown(rep, inputs), encoding="utf-8")
    rep["pdf_check"]["pdf"] = inputs["cv"]
    md_path.with_suffix(".json").write_text(json.dumps({**inputs, **rep}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    c, cov = rep["counts"], rep["evidence_coverage"]
    errors = sum(f["severity"] == "error" for f in rep["pdf_check"]["findings"])
    print(f"{rep['title']}\n  PDF: {errors} error(s), "
          f"{sum(f['severity'] == 'warning' for f in rep['pdf_check']['findings'])} warning(s)")
    print(f"  Requirements: {c['met']} met, {c['partial']} partial, {c['missing']} missing, {c['uncertain']} uncertain "
          f"({rep['overridden']} overridden)")
    print(f"  Evidence coverage v{cov['version']}: must-have {cov['must_have']}, preferred {cov['preferred']} (not an ATS score)")
    print(f"  Report: {rel(md_path)} (+ .json)")
    sys.exit(1 if errors or not rep["pdf_check"]["pages"] else 0)


if __name__ == "__main__":
    main()
