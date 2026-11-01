#!/usr/bin/env python3
"""Writing-style warnings for a resume content file (ATS reviewer).

Usage: python3 check_style.py [content/default.json] [--out report.json]

These help the recruiter who reads the resume after the ATS has parsed it. They are
rule-based advice, never errors: style is your call. Always exits 0.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIRST_PERSON = re.compile(r"\b(I|I'm|I've|me|my|mine|we|our|us)\b")  # case-sensitive: "I" not "i"
WEAK_OPENERS = ("helped", "contributed", "assisted", "worked on", "participated", "involved in",
                "responsible for", "tasked with", "in charge of", "supported")
RESULT = re.compile(r"\d|%|\b(one|two|three|four|five|six|seven|eight|nine|ten|dozens?|hundreds?|thousands?)\b", re.I)
MAX_BULLET_WORDS = 30
MAX_SUMMARY_WORDS = 60


def check(content: dict) -> dict:
    findings = []

    def add(severity, code, field, message):
        findings.append({"severity": severity, "code": code, "field": field, "message": f"{field}: {message}"})

    summary = content.get("summary", "")
    if FIRST_PERSON.search(summary):
        found = sorted(set(FIRST_PERSON.findall(summary)))
        add("warning", "first_person", "summary", f"uses first person ({', '.join(found)}). Resume convention drops it: "
            "'Business-oriented developer who partners with teams…'.")
    if len(summary.split()) > MAX_SUMMARY_WORDS:
        add("warning", "too_long", "summary", f"{len(summary.split())} words; keep it under {MAX_SUMMARY_WORDS}.")

    lines = []  # (field, text) for every description and bullet
    for i, job in enumerate(content.get("experience", [])):
        if job.get("description"):
            lines.append((f"experience[{i}].description ({job['company'].strip(' ,')})", job["description"]))
        lines += [(f"experience[{i}].bullets[{j}] ({job['company'].strip(' ,')})", b) for j, b in enumerate(job.get("bullets", []))]

    for field, text in lines:
        words = text.split()
        opener = text.casefold()
        weak = next((w for w in WEAK_OPENERS if opener.startswith(w)), None)
        if weak:
            add("warning", "weak_opener", field, f"starts with '{text[:len(weak)]}'. Lead with what you did "
                "(Built, Shipped, Led, Reduced…) so your own part is clear.")
        if FIRST_PERSON.search(text):
            add("warning", "first_person", field, "uses first person; resume lines usually drop it.")
        if field.split(" ")[0].endswith("]") and len(words) > MAX_BULLET_WORDS:
            add("warning", "too_long", field, f"{len(words)} words; bullets over {MAX_BULLET_WORDS} get skimmed. Split or trim.")

    measured = [f for f, t in lines if RESULT.search(t)]
    if lines:
        add("info", "measurable", "experience", f"{len(measured)} of {len(lines)} lines include a number or measurable "
            "result. Recruiters look for scale and outcomes (users, clients, %, time saved) where you truthfully have them.")
    openers = Counter(t.split()[0].strip(",").casefold() for _, t in lines if t.split())
    for verb, n in openers.items():
        if n >= 3:
            add("info", "repeated_opener", "experience", f"{n} lines start with '{verb.capitalize()}'; vary the verbs.")
    return {"findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("content", nargs="?", type=Path, default=HERE / "content" / "default.json")
    parser.add_argument("--out", type=Path, help="JSON report path (default: analysis/<content name>.style.json)")
    args = parser.parse_args()

    report = check(json.loads(args.content.read_text(encoding="utf-8")))
    path = args.content.resolve()
    report["content"] = str(path.relative_to(HERE)) if path.is_relative_to(HERE) else str(args.content)
    out = args.out or HERE / "analysis" / f"{args.content.stem}.style.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for f in report["findings"]:
        print(f"[{f['severity']}] {f['message']}")
    warnings = sum(f["severity"] == "warning" for f in report["findings"])
    print(f"\n{warnings} style warning(s). Report: {out}")


if __name__ == "__main__":
    main()
