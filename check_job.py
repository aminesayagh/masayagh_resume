#!/usr/bin/env python3
"""Validate a job requirements file before it is used for scoring (ATS reviewer, milestone 2).

Usage: python3 check_job.py jobs/<job-slug>.json [--draft]

A job file lists what a posting asks for. Every requirement must quote the posting
verbatim, so each later finding traces back to the employer's own words, and a human
must mark it reviewed. See docs/job-file-guide.md.
Exit code: 0 = valid, 1 = errors. --draft reports unreviewed requirements as warnings.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTIONS = {"responsibility", "requirement", "preferred", "location", "screening"}
PRIORITIES = {"must_have", "preferred"}
KINDS = {"evidence", "years_experience"}
STATUSES = {"met", "partial", "missing", "uncertain"}
OVERRIDE_FIELDS = {"id", "status", "reason", "pdf_quote"}
FIELDS = {"id", "section", "priority", "quote", "description", "terms", "kind", "min_years", "reviewed", "note"}
# Wording that signals a wish, not a gate. A must_have quoting it is an inferred hard gate.
SOFT_WORDING = re.compile(r"\b(nice to have|a plus|bonus|ideally|preferred|preferably|desirable)\b", re.I)


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text).strip().casefold()


def posting_text(job: dict, root: Path) -> str | None:
    if "posting_text" in job:
        return job["posting_text"]
    if "posting_file" in job:
        path = root / job["posting_file"]
        return path.read_text(encoding="utf-8") if path.exists() else None
    return None


def validate(job: dict, root: Path = HERE, draft: bool = False) -> list[dict]:
    findings = []

    def add(severity, code, message, rid=None):
        findings.append({"severity": severity, "code": code, "id": rid, "message": f"{rid}: {message}" if rid else message})

    if not isinstance(job, dict):
        add("error", "shape", "The job file must be a JSON object.")
        return findings
    if not job.get("title"):
        add("error", "title", "Missing 'title' (company and role).")
    text = posting_text(job, root)
    if text is None:
        add("error", "posting", "Missing posting: set 'posting_text', or 'posting_file' pointing to an existing file.")
    posting = norm(text or "")
    reqs = job.get("requirements")
    if not isinstance(reqs, list) or not reqs:
        add("error", "requirements", "'requirements' must be a non-empty list.")
        return findings

    seen = set()
    for i, r in enumerate(reqs):
        rid = r.get("id") if isinstance(r, dict) else None
        if not isinstance(r, dict) or not isinstance(rid, str) or not rid:
            add("error", "id", f"requirements[{i}] needs a string 'id'.")
            continue
        if rid in seen:
            add("error", "id_duplicate", "duplicate id; ids must be unique and stable.", rid)
        seen.add(rid)
        for key in sorted(set(r) - FIELDS):
            add("error", "unknown_field", f"unknown field '{key}' (typo?).", rid)
        if r.get("section") not in SECTIONS:
            add("error", "section", f"'section' must be one of {sorted(SECTIONS)}.", rid)
        if r.get("priority") not in PRIORITIES:
            add("error", "priority", f"'priority' must be one of {sorted(PRIORITIES)}.", rid)
        if not r.get("description"):
            add("error", "description", "missing a short 'description'.", rid)

        quote = r.get("quote") or ""
        if not quote.strip():
            add("error", "quote_missing", "no source quote; every requirement must quote the posting.", rid)
        elif text is not None and norm(quote) not in posting:
            add("error", "quote_not_found", f"quote not found verbatim in the posting: '{quote}'.", rid)

        if r.get("priority") == "must_have":
            if r.get("section") == "preferred":
                add("error", "soft_gate", "listed under preferred qualifications but marked must_have.", rid)
            elif SOFT_WORDING.search(quote):
                add("error", "soft_gate", f"quote uses soft wording ('{SOFT_WORDING.search(quote).group()}') but is marked "
                    "must_have; do not infer a hard gate from vague language.", rid)

        terms = r.get("terms", [])
        if not isinstance(terms, list) or not all(isinstance(t, str) and t.strip() for t in terms):
            add("error", "terms", "'terms' must be a list of non-empty strings.", rid)
        else:
            for t in terms:
                if norm(t) not in norm(quote):
                    add("error", "term_not_in_quote", f"term '{t}' is not in the quote; use the posting's exact wording.", rid)

        kind = r.get("kind", "evidence")
        if kind not in KINDS:
            add("error", "kind", f"'kind' must be one of {sorted(KINDS)}.", rid)
        elif kind == "years_experience":
            if not isinstance(r.get("min_years"), (int, float)) or r["min_years"] <= 0:
                add("error", "min_years", "years_experience needs a positive number 'min_years'.", rid)
        elif not terms:
            add("error", "terms", "an evidence requirement needs at least one search term.", rid)

        if r.get("reviewed") is not True:
            add("warning" if draft else "error", "unreviewed", "not reviewed; check the quote and priority against "
                "the posting, then set \"reviewed\": true.", rid)

    overrides = job.get("overrides", [])
    if not isinstance(overrides, list):
        add("error", "overrides", "'overrides' must be a list.")
        return findings
    overridden = set()
    for i, o in enumerate(overrides):
        oid = o.get("id") if isinstance(o, dict) else None
        label = f"overrides[{i}]"
        if oid not in seen:
            add("error", "override_id", f"{label} refers to unknown requirement id '{oid}'.")
            continue
        if oid in overridden:
            add("error", "override_duplicate", f"{label}: more than one override for this requirement.", oid)
        overridden.add(oid)
        for key in sorted(set(o) - OVERRIDE_FIELDS):
            add("error", "unknown_field", f"{label}: unknown field '{key}' (typo?).", oid)
        if o.get("status") not in STATUSES:
            add("error", "override_status", f"{label}: 'status' must be one of {sorted(STATUSES)}.", oid)
        if not str(o.get("reason") or "").strip():
            add("error", "override_reason", f"{label}: an override needs a 'reason'.", oid)
        if o.get("pdf_quote") is not None and not isinstance(o["pdf_quote"], str):
            add("error", "override_quote", f"{label}: 'pdf_quote' must be the PDF text the decision relies on, or null.", oid)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("job", type=Path)
    parser.add_argument("--draft", action="store_true", help="allow unreviewed requirements (warnings)")
    args = parser.parse_args()

    try:
        job = json.loads(args.job.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[error] {args.job}: {exc}")
        sys.exit(1)
    findings = validate(job, draft=args.draft)
    for f in findings:
        print(f"[{f['severity']}] {f['message']}")
    reqs = job.get("requirements") or []
    by = lambda key, value: sum(isinstance(r, dict) and r.get(key) == value for r in reqs)
    errors = sum(f["severity"] == "error" for f in findings)
    print(f"\n{len(reqs)} requirement(s): {by('priority', 'must_have')} must-have, {by('priority', 'preferred')} preferred; "
          f"{by('reviewed', True)} reviewed. {errors} error(s).")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
