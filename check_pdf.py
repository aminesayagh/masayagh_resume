#!/usr/bin/env python3
"""Check that a generated resume PDF reads back as clean text (ATS reviewer, milestone 1).

Usage: python3 check_pdf.py [output/default.pdf] [--content content/default.json] [--out report.json]

This checks parseability only: whether the text an ATS parser would extract matches the
resume content. It never claims compatibility with any employer's ATS.
Exit code: 0 = no errors (warnings allowed), 1 = errors found.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template" / "resume.html"

# Section names most resume parsers recognise. Heading text outside this list may still
# parse, but it is a gamble, so it is reported as a warning.
STANDARD_HEADINGS = {
    "summary": {"summary", "professional summary", "profile"},
    "skills": {"skills", "technical skills"},
    "experience": {"experience", "work experience", "professional experience"},
    "education": {"education"},
    "languages": {"languages"},
}
MIN_CHARS_PER_PAGE = 50  # below this a page is almost certainly an image or empty


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text).strip().casefold()


def template_headings(template: Path) -> list[str]:
    html = template.read_text(encoding="utf-8")
    static = re.findall(r'class="title_h3">([^<$]*(?:<br\s*/?>[^<$]*)*)</h3>', html)
    dynamic = re.findall(r"appendItems\('[^']+',\s*'([^']+)'\)", html)
    return [re.sub(r"<br\s*/?>", " ", h).strip() for h in static + dynamic]


def find(needle: str, lines: list[str], joined: str) -> str:
    """'line' if the text sits on one extracted line, 'split' if only across lines, else 'missing'."""
    n = norm(needle)
    if any(n in line for line in lines):
        return "line"
    return "split" if n in joined else "missing"


def check(pdf: Path, content: dict | None, headings: list[str]) -> dict:
    findings = []

    def add(severity, code, message, **extra):
        findings.append({"severity": severity, "code": code, "message": message, **extra})

    try:
        pages = [p.extract_text() or "" for p in PdfReader(pdf).pages]
    except Exception as exc:  # unreadable file is the one thing every ATS fails on
        add("error", "unreadable", f"PDF could not be read: {exc}")
        return {"pdf": str(pdf), "pages": [], "findings": findings}

    for i, text in enumerate(pages, 1):
        if len(text.strip()) < MIN_CHARS_PER_PAGE:
            add("error", "no_text", f"Page {i} has almost no extractable text; it may be an image. "
                "Export the PDF from HTML/text, not as a scan or screenshot.", page=i)

    lines = [norm(l) for t in pages for l in t.splitlines() if l.strip()]
    joined = " ".join(lines)

    def require(label, value, severity="error"):
        if not value:
            return
        where = find(value, lines, joined)
        if where == "missing":
            add(severity, "field_missing", f"{label} '{value}' not found in the PDF text.")
        elif where == "split":
            add("warning", "field_split", f"{label} '{value}' is broken across lines; a parser may read it as two values. "
                "Keep it on one line (shorter text or a wider column).")

    for h in headings:
        require("Heading", h, "warning")
        if not any(norm(h) in names for names in STANDARD_HEADINGS.values()):
            add("warning", "heading_nonstandard", f"Heading '{h}' is not a common section name; parsers look for e.g. "
                + ", ".join(sorted(n.title() for names in STANDARD_HEADINGS.values() for n in names if " " not in n)) + ".")

    if content:
        c = content.get("contact", {})
        require("Name", content.get("name"))
        for key in ("email", "phone", "location"):
            require(key.capitalize(), c.get(key))
        positions = []
        for job in content.get("experience", []):
            company = job["company"].strip(" ,")
            require("Company", company)
            require(f"Dates for {company}", job["dates"])
            require(f"Role at {company}", job["role"])
            if not job["role"].strip():
                add("warning", "role_missing", f"'{company}' has no job title; parsers expect title, company and dates per entry.")
            starts = [i for i, l in enumerate(lines) if l.startswith(norm(company))]
            if len(starts) > 1:
                add("warning", "entry_repeated", f"'{company}' starts {len(starts)} lines; a parser may record it as "
                    "separate jobs. Avoid repeating the entry header when a job continues on the next page.")
            positions.append((company, starts[0] if starts else None))
        found = [(c_, p) for c_, p in positions if p is not None]
        for (a, pa), (b, pb) in zip(found, found[1:]):
            if pb < pa:
                add("warning", "order", f"'{b}' is extracted before '{a}', unlike the content order.")
        for entry in content.get("education", []):
            require("Degree", entry["degree"])
            require(f"Dates for {entry['degree']}", entry["dates"], "warning")

    if len(pages) > 1:  # first/last line repeated on every page = header/footer; digits ignored so "P1"/"P2" match
        edges = [[l for l in t.splitlines() if l.strip()] for t in pages]
        per_page = [{re.sub(r"\d+", "#", norm(l)) for l in e[:1] + e[-1:]} for e in edges]
        for line in sorted(set.intersection(*per_page)):
            add("info", "repeated_line", f"'{line}' appears on every page (header/footer?). Usually harmless, "
                "but some parsers fold it into the surrounding section.")

    return {"pdf": str(pdf), "pages": [{"page": i, "chars": len(t)} for i, t in enumerate(pages, 1)], "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", nargs="?", type=Path, default=HERE / "output" / "default.pdf")
    parser.add_argument("--content", type=Path, help="content JSON (default: content/<pdf name>.json if present)")
    parser.add_argument("--out", type=Path, help="JSON report path (default: analysis/<pdf name>.pdf-check.json)")
    args = parser.parse_args()

    content_path = args.content or HERE / "content" / f"{args.pdf.stem}.json"
    content = json.loads(content_path.read_text(encoding="utf-8")) if content_path.exists() else None
    report = check(args.pdf, content, template_headings(TEMPLATE))
    rel = lambda path: str(path.resolve().relative_to(HERE)) if path.resolve().is_relative_to(HERE) else str(path)
    report["pdf"], report["content"] = rel(args.pdf), rel(content_path) if content else None

    out = args.out or HERE / "analysis" / f"{args.pdf.stem}.pdf-check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if not content:
        print(f"note: no content file at {content_path}; field checks skipped")
    for f in report["findings"]:
        print(f"[{f['severity']}] {f['message']}")
    counts = {s: sum(f["severity"] == s for f in report["findings"]) for s in ("error", "warning", "info")}
    print(f"\n{len(report['pages'])} page(s); {counts['error']} error(s), {counts['warning']} warning(s), "
          f"{counts['info']} info. Report: {out}")
    print("This checks text extraction only; it is not a score from any employer's ATS.")
    sys.exit(1 if counts["error"] else 0)


if __name__ == "__main__":
    main()
