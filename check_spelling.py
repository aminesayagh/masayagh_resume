#!/usr/bin/env python3
"""Spell-check a resume content file before building the PDF (ATS reviewer, step 0).

Usage: python3 check_spelling.py [content/default.json] [--out report.json]

Every unknown word is a WARNING with suggested fixes, never an error: product names,
tech terms and proper nouns are often correct even when the dictionary does not know them.
Add words you have confirmed to spelling-allow.txt (one per line) to silence them.
Always exits 0.
"""

import argparse
import json
import re
from pathlib import Path

from spellchecker import SpellChecker

import check_pdf

HERE = Path(__file__).resolve().parent
ALLOW_FILE = HERE / "spelling-allow.txt"
SKIP_KEYS = {"email", "phone", "phone_link", "website", "website_link", "github", "linkedin", "qr_url", "dates"}
# Names, not prose: their words are trusted, so a company or skill never warns.
TRUSTED_KEYS = {"name", "company", "detail", "institution", "location", "language", "level", "skills"}
WORD = re.compile(r"[A-Za-z][A-Za-z'’]*")


def strings(node, path=""):
    """Yield (path, key, text) for every string in the content JSON."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from ((p, k or key, t) for p, k, t in strings(value, f"{path}.{key}" if path else key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from strings(value, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, None, node


def words(text):
    for m in WORD.finditer(text):
        word = m.group().replace("’", "'")
        word = re.sub(r"'s$", "", word).strip("'")
        # ponytail: skip acronyms (API, SaaS) and internal-caps names (FastAPI, WordPress); a dictionary can't judge them
        if not word or word.isupper() or any(c.isupper() for c in word[1:]):
            continue
        if text[m.end():m.end() + 1] == "." and text[m.end() + 1:m.end() + 2].isalpha():
            continue  # Next.js, Vue.js
        yield word, m.start()


def check(content: dict, headings: list[str], allow: set[str]) -> dict:
    spell = SpellChecker()  # English
    items = [(p, k, t) for p, k, t in strings(content) if k not in SKIP_KEYS]
    trusted = {w.casefold() for p, k, t in items if k in TRUSTED_KEYS or p.startswith("skills")
               for w, _ in words(t)}
    known = trusted | {w.casefold() for w in allow}
    items += [(f"template heading '{h}'", None, h) for h in headings]

    findings = []
    for path, key, text in items:
        if key in TRUSTED_KEYS or path.startswith("skills"):
            continue
        for word, at in words(text):
            lower = word.casefold()
            singular = lower.removesuffix("s")
            if {lower, singular} & known or spell.known([lower]) or spell.known([singular]):
                continue
            suggestions = sorted(spell.candidates(lower) or [], key=spell.word_usage_frequency, reverse=True)[:3]
            findings.append({
                "severity": "warning", "code": "spelling", "word": word, "field": path,
                "context": text[max(0, at - 30):at + len(word) + 30].strip(),
                "suggestions": suggestions,
                "message": f"'{word}' in {path} is not in the dictionary"
                + (f"; did you mean {', '.join(repr(s) for s in suggestions)}?" if suggestions else "; no suggestion.")
                + " Ignore it if the word is correct (name or term), or add it to spelling-allow.txt.",
            })
    return {"findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("content", nargs="?", type=Path, default=HERE / "content" / "default.json")
    parser.add_argument("--out", type=Path, help="JSON report path (default: analysis/<content name>.spelling.json)")
    args = parser.parse_args()

    content = json.loads(args.content.read_text(encoding="utf-8"))
    allow = set()
    if ALLOW_FILE.exists():
        allow = {l.strip() for l in ALLOW_FILE.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}
    report = check(content, check_pdf.template_headings(check_pdf.TEMPLATE), allow)
    path = args.content.resolve()
    report["content"] = str(path.relative_to(HERE)) if path.is_relative_to(HERE) else str(args.content)

    out = args.out or HERE / "analysis" / f"{args.content.stem}.spelling.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for f in report["findings"]:
        print(f"[warning] {f['message']}\n          ...{f['context']}...")
    print(f"\n{len(report['findings'])} spelling warning(s). Report: {out}")


if __name__ == "__main__":
    main()
