#!/usr/bin/env python3
"""After any edit to a job's content.json: build, review, publish, and print the full gap table.

Usage: python3 src/tailor.py jobs/<slug>

1. Builds the PDF (which re-runs the review and refreshes review.md/json, interview.json, dashboard.html).
2. Publishes it to the portfolio, unless it is over 3 pages or has PDF errors.
3. Prints every requirement that is not met: priority, status, each term, and the resume sections it is
   still missing from. This table is the pipeline's output; show it as-is.
"""

import json
import sys
from pathlib import Path

import build_resume
import publish_resume


def gap_table(review: dict) -> list[str]:
    rows = ["| Req | Priority | Status | Term | Term status | Missing from |", "|---|---|---|---|---|---|"]
    for r in review["results"]:
        if r["status"] == "met":
            continue
        terms = r.get("terms") or [{"term": f"({r.get('description', '')})", "status": r["status"], "missing_from": []}]
        for t in terms:
            if t["status"] == "met" and not t.get("missing_from"):
                continue
            rows.append(f"| {r['id']} | {r['priority'].replace('_', '-')} | {r['status']} | {t['term']} | {t['status']} | "
                        f"{', '.join(t.get('missing_from') or []) or '-'} |")
    return rows


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = Path(sys.argv[1])
    job_path = folder / "job.json"
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if not job.get("requirements"):
        sys.exit("No requirements yet: draft them first (job-requirements agent).")

    build_resume.build(folder / "content.json")
    review = json.loads((folder / "review.json").read_text(encoding="utf-8"))
    pages = len(review["pdf_check"]["pages"])
    errors = sum(f["severity"] == "error" for f in review["pdf_check"]["findings"])
    if pages > build_resume.MAX_PAGES or errors:
        print(f"\nNOT published: {pages} pages, {errors} PDF error(s). Fix that first.")
    else:
        publish_resume.publish(job_path)

    rows = gap_table(review)
    cov, c = review["evidence_coverage"], review["counts"]
    print(f"\n{job['title']}: {c['met']} met, {c['partial']} partial, {c['missing']} missing "
          f"(matcher v{review['match_version']}); evidence coverage must-have {cov['must_have']}, "
          f"preferred {cov['preferred']} = {cov['formula']}, not an ATS score.")
    print("\nEverything not met:" if len(rows) > 2 else "\nEvery requirement is met.")
    if len(rows) > 2:
        print("\n".join(rows))
    print(f"\nDashboard: {folder / 'dashboard.html'} (built from this same review)")


if __name__ == "__main__":
    main()
