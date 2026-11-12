#!/usr/bin/env python3
"""Mechanical help for drafting a job file's requirements, so a small model only makes judgement calls.

Usage:
  python3 src/draft_job.py lines  jobs/<slug>/job.json              # numbered posting lines with their heading
  python3 src/draft_job.py apply  jobs/<slug>/job.json DRAFT.json   # build requirements from line numbers
  python3 src/draft_job.py missed jobs/<slug>/job.json              # candidate terms no requirement covers

DRAFT.json is a list of picks; the script copies each quote from its line, so quotes are always verbatim:
  [{"line": 14, "terms": ["Vue 3"], "priority": "must_have", "section": "requirement",
    "targets": ["skills", "experience"], "description": "Vue 3 in production"},
   {"line": 9, "kind": "years_experience", "min_years": 5, "priority": "must_have",
    "section": "requirement", "description": "5+ years of front-end development"}]
Optional per pick: "note". Terms the drafter decides to leave out go in the offer's "skipped_terms"
({"term": "reason"}), so `missed` stops listing them.
"""

import json
import re
import sys
from pathlib import Path

import check_job
import offers

ROOT = Path(__file__).resolve().parent.parent
BULLET = re.compile(r"^\s*(?:[·•\-\*–—]|\d+[.)])\s*")
PICK_FIELDS = {"line", "terms", "priority", "section", "targets", "description", "kind", "min_years", "note"}
# Capitalised words that start sentences or headings, not technologies.
COMMON = set("""a an and are as at be build by can for from have in is it its of on or our the this to we what will with
you your about all also any as both but day each every first from here how if into its job just more most must new
not now one only other out over own per role same some such team than that their them then there these they those
through up us very well when where which while who why work years""".split())


def posting_lines(job: dict) -> list[dict]:
    """Every non-empty posting line: number, the heading above it, the text without its bullet marker."""
    out, heading = [], ""
    for raw in (check_job.posting_text(job, ROOT) or "").splitlines():
        text = BULLET.sub("", raw).strip()
        if not text:
            continue
        is_heading = not BULLET.match(raw) and len(text) <= 60 and not text.endswith((".", ","))
        out.append({"line": len(out) + 1, "heading": heading, "text": text, "is_heading": is_heading})
        if is_heading:
            heading = text.rstrip(":")
    return out


def term_problems(term: str) -> str | None:
    """Terms are what a recruiter types into a search box: short, one thing each."""
    one_acronym = re.fullmatch(r"[A-Z]{1,4}/[A-Z]{1,4}", term)  # CI/CD, TCP/IP are one thing
    if ("/" in term and not one_acronym) or re.search(r"\b(and|or)\b", term):
        return f"term '{term}' joins several things; split it into separate terms"
    if len(term.split()) > 3:
        return f"term '{term}' is a phrase; use the 1-3 word name a recruiter searches for"
    return None


def apply(job: dict, picks: list[dict]) -> list[dict]:
    lines = {l["line"]: l for l in posting_lines(job)}
    reqs = []
    for i, pick in enumerate(picks, 1):
        if set(pick) - PICK_FIELDS or pick.get("line") not in lines:
            raise ValueError(f"pick {i}: unknown field or line number: {pick}")
        if not pick.get("terms"):  # a requirement is a keyword; "5+ years of Java" names Java too
            raise ValueError(f"pick {i} (line {pick['line']}) has no terms; name what a recruiter would search for")
        for term in pick.get("terms", []):
            if problem := term_problems(term):
                raise ValueError(f"pick {i} (line {pick['line']}): {problem}")
        req = {"id": f"R{i:02d}", "section": pick.get("section", "requirement"), "priority": pick["priority"],
               "quote": lines[pick["line"]]["text"], "description": pick.get("description", ""),
               "terms": pick.get("terms", [])}
        for key in ("targets", "kind", "min_years", "note"):
            if key in pick:
                req[key] = pick[key]
        req["reviewed"] = False
        reqs.append(req)
    return reqs


DEGREE = re.compile(r"\b(bachelor|master|degree|diploma|bac\s*\+)", re.I)


def coverage_errors(job: dict, reqs: list[dict]) -> list[str]:
    """Rules a small model tends to skip, enforced here: the job location and every degree line need a requirement."""
    errors, quotes = [], {r["quote"] for r in reqs}
    location = job.get("location") or next((l["text"].split(":", 1)[1].strip() for l in posting_lines(job)
                                            if l["text"].casefold().startswith("location:")), "")
    if location and not any(r["section"] == "location" for r in reqs):
        errors.append(f"no 'location' requirement; the job is in '{location}' (section 'location', term = the city)")
    for l in posting_lines(job):
        if not l["is_heading"] and DEGREE.search(l["text"]) and l["text"] not in quotes:
            errors.append(f"line {l['line']} asks for a degree but has no requirement: '{l['text'][:80]}'")
    return errors


TECH = re.compile(r"(?<![\w.])(?:[A-Za-z][\w]*(?:[./+#-][\w+#]+)+\+?|[A-Z][a-z]*[A-Z]\w*|[a-z]+[A-Z]\w*|[A-Z]{2,}\d*s?"
                  r"|[A-Z][a-z]+(?: \d+)?)(?![\w])")


def candidates(job: dict) -> list[str]:
    """Technology-looking words in requirement lines: CamelCase, acronyms, dotted/slashed names, capitalised words
    that don't start the line. A naive filter: it over-lists on purpose, the drafter decides."""
    found = {}
    for l in posting_lines(job):
        if l["is_heading"]:
            continue
        for m in TECH.finditer(l["text"]):
            word = m.group().strip(".-/")
            starts_line = m.start() == 0 or l["text"][:m.start()].rstrip().endswith((".", ":", "!", "?"))
            plain_capital = re.fullmatch(r"[A-Z][a-z]+", word)
            if (word.casefold() in COMMON or len(word) < 2 or (plain_capital and starts_line)
                    or re.fullmatch(r"[a-z]+(?:-[a-z]+)+", word)                     # back-end, mid-level
                    or re.search(r"https?:|www\.|\.(?:com|io|co|org|net|fr|ma)\b|^e\.g$", word)):
                continue
            found.setdefault(word.casefold(), word)
    return sorted(found.values(), key=str.casefold)


def missed(job: dict) -> list[str]:
    covered = " | ".join(t.casefold() for r in job.get("requirements", []) for t in r.get("terms", []))
    skipped = {k.casefold() for k in job.get("skipped_terms", {})}
    def is_covered(c: str) -> bool:  # "JavaScript/TypeScript" is covered when both parts are
        return c.casefold() in skipped or all(part.casefold() in covered for part in c.split("/") if part.strip())
    return [c for c in candidates(job) if not is_covered(c)]


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in {"lines", "apply", "missed"}:
        sys.exit(__doc__)
    path = Path(sys.argv[2])
    job = offers.read(path)
    if sys.argv[1] == "lines":
        for l in posting_lines(job):
            print(f"{'#' if l['is_heading'] else ' '}{l['line']:>3} [{l['heading']}] {l['text']}")
    elif sys.argv[1] == "apply":
        try:
            job["requirements"] = apply(job, json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")))
        except ValueError as exc:
            sys.exit(f"[error] {exc}")
        offers.write(path, job)
        errors = [f["message"] for f in check_job.validate(job, ROOT, draft=True) if f["severity"] == "error"]
        errors += coverage_errors(job, job["requirements"])
        print(f"{len(job['requirements'])} requirement(s) written to {path}; {len(errors)} error(s).")
        for message in errors:
            print(f"  [error] {message}")
        sys.exit(1 if errors else 0)
    left = missed(job)
    print("\n".join(left) if left else "Every candidate term is covered or skipped with a reason.")


_JOB = {"posting_text": "Essential\n· 2+ years with Vue 3 and Node.js in production\n· Strong CI/CD skills\nWe value TypeScript.",
        "requirements": []}
assert [l["text"] for l in posting_lines(_JOB)][1] == "2+ years with Vue 3 and Node.js in production"
assert posting_lines(_JOB)[1]["heading"] == "Essential"
assert set(candidates(_JOB)) >= {"Vue 3", "Node.js", "CI/CD", "TypeScript"}, candidates(_JOB)
_LOC = {"posting_text": "Location: Rabat, Morocco\nRequirements\n· Bachelor's degree in computer science", "requirements": []}
assert len(coverage_errors(_LOC, [])) == 2
assert coverage_errors(_LOC, [{"section": "location", "quote": "Location: Rabat, Morocco"},
                              {"section": "requirement", "quote": "Bachelor's degree in computer science"}]) == []
assert term_problems("JavaScript/TypeScript") and term_problems("full-stack software development expertise")
assert term_problems("Vue 3") is None and term_problems("CI/CD") is None
assert apply(_JOB, [{"line": 2, "terms": ["Vue 3"], "priority": "must_have"}])[0]["quote"] == "2+ years with Vue 3 and Node.js in production"

if __name__ == "__main__":
    main()
