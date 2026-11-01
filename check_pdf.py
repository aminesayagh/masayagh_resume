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
import urllib.error
import urllib.request
from datetime import date
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


MONTHS = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
DATE = re.compile(r"^(?:([A-Za-z]{3})[a-z]*\.? )?(\d{4})$")


def parse_month(text: str, end: bool) -> int | None:
    """'Jul 2024' -> month index (year*12+month); 'Present' -> this month; '2024' -> Jan/Dec."""
    text = text.strip()
    if text.casefold() in {"present", "now", "current"}:
        return date.today().year * 12 + date.today().month
    m = DATE.match(text)
    if not m or (m.group(1) and m.group(1).casefold() not in MONTHS):
        return None
    month = MONTHS[m.group(1).casefold()] if m.group(1) else (12 if end else 1)
    return int(m.group(2)) * 12 + month


def check_dates(content: dict, add) -> dict:
    today = date.today().year * 12 + date.today().month
    spans = []
    for job in content.get("experience", []):
        company, raw = job["company"].strip(" ,"), job["dates"]
        parts = re.split(r"\s*[-\u2013\u2014]\s*|\s+to\s+", raw)
        if len(parts) == 1:
            add("warning", "date_single", f"'{company}' has a single date '{raw}'; parsers expect a range "
                "('Aug 2021 - Aug 2021' or 'Aug 2021 - Sep 2021') to compute its length.")
            parts = parts * 2
        start, end = parse_month(parts[0], False), parse_month(parts[-1], True)
        if start is None or end is None:
            add("warning", "date_format", f"'{company}' dates '{raw}' are not in 'Mon YYYY - Mon YYYY' form; a parser may not read them.")
            continue
        if start > end:
            add("warning", "date_order", f"'{company}' starts after it ends: '{raw}'.")
            continue
        if start > today or (end > today and "present" not in raw.casefold()):
            add("warning", "date_future", f"'{company}' has a date in the future: '{raw}'.")
        spans.append((company, start, end + 1))  # end month is inclusive
    pairs = [f"{a} / {b}" for i, (a, s1, e1) in enumerate(spans) for b, s2, e2 in spans[i + 1:] if s1 < e2 and s2 < e1]
    if pairs:
        add("info", "date_overlap", f"{len(pairs)} overlapping job pair(s): {'; '.join(pairs)}. Fine for parallel work, "
            "but some parsers add overlapping jobs twice when computing years of experience.", pairs=pairs)
    merged, cur = 0, None
    for _, s_, e_ in sorted(spans, key=lambda span: span[1]):
        if cur and s_ <= cur[1]:
            cur[1] = max(cur[1], e_)
        else:
            merged += cur[1] - cur[0] if cur else 0
            cur = [s_, e_]
    merged += cur[1] - cur[0] if cur else 0
    summed = sum(e_ - s_ for _, s_, e_ in spans)
    years = {"merged": round(merged / 12, 1), "summed": round(summed / 12, 1)}
    if spans:
        add("info", "experience_years", f"Experience from your dates: {years['merged']} years counting overlaps once, "
            f"{years['summed']} years if a parser adds every job. Requirements like '3+ years' are filtered on numbers like these.")
    return years


def check_contact(content: dict, joined: str, uris: set[str], add, network: bool) -> None:
    c = content.get("contact", {})
    email, phone = c.get("email", ""), c.get("phone", "")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email, re.I):
        add("warning", "email_format", f"Email '{email}' does not look like a valid address.")
    digits = re.sub(r"\D", "", phone)
    if phone and not 8 <= len(digits) <= 15:
        add("warning", "phone_format", f"Phone '{phone}' has {len(digits)} digits; international numbers have 8-15.")
    elif phone and not phone.lstrip().startswith(("+", "(+", "00")):
        add("warning", "phone_country", f"Phone '{phone}' has no country code; add it for employers abroad.")
    for key in ("linkedin", "github", "website_link"):
        url = c.get(key)
        if not url:
            continue
        bare = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
        if norm(bare) not in joined:
            add("warning", "link_icon_only", f"{key} '{bare}' is not written as text in the PDF (only as a clickable "
                "icon, if at all). Parsers read text, not icons; write the address out so it is captured.")
        if url.rstrip("/") not in {u.rstrip("/") for u in uris}:
            add("info", "link_not_clickable", f"{key} '{url}' is not a clickable link in the PDF.")
        if network:
            check_url(key, url, add)


def check_url(key: str, url: str, add) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (resume link check)"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            status = resp.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        add("warning", "link_unreachable", f"{key} '{url}' could not be opened: {exc}. Check it in a browser.")
        return
    if status in (403, 429, 999):  # LinkedIn and others block scripts; not proof the page is broken
        add("info", "link_unverified", f"{key} '{url}' refused an automated check (HTTP {status}); open it in a browser to confirm.")
    elif status >= 400:
        add("warning", "link_broken", f"{key} '{url}' returned HTTP {status}.")


def check_metadata(reader: PdfReader, pdf: Path, content: dict | None, add) -> None:
    meta = reader.metadata or {}
    name = (content or {}).get("name", "")
    title = meta.get("/Title") or ""
    if not title.strip():
        add("warning", "meta_title", "The PDF has no title; some ATS and email clients show 'Untitled'.")
    elif name and norm(name) not in norm(title):
        add("warning", "meta_title", f"PDF title '{title}' does not contain your name.")
    if not (meta.get("/Author") or "").strip():
        add("info", "meta_author", "The PDF has no author field; set it to your name.")
    if name and not any(part.casefold() in pdf.stem.casefold() for part in name.split() if len(part) > 2):
        add("warning", "file_name", f"File name '{pdf.name}' does not contain your name; recruiters see it on upload. "
            f"Rename it, e.g. '{'-'.join(name.split())}-Resume.pdf'.")


def check(pdf: Path, content: dict | None, headings: list[str], network: bool = False) -> dict:
    findings = []

    def add(severity, code, message, **extra):
        findings.append({"severity": severity, "code": code, "message": message, **extra})

    try:
        reader = PdfReader(pdf)
        pages = [p.extract_text() or "" for p in reader.pages]
        uris = {str(a.get_object().get("/A", {}).get("/URI", "")) for p in reader.pages for a in (p.get("/Annots") or [])}
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

    years = None
    if content:
        check_contact(content, joined, uris, add, network)
        years = check_dates(content, add)
    check_metadata(reader, pdf, content, add)

    if len(pages) > 1:  # first/last line repeated on every page = header/footer; digits ignored so "P1"/"P2" match
        edges = [[l for l in t.splitlines() if l.strip()] for t in pages]
        per_page = [{re.sub(r"\d+", "#", norm(l)) for l in e[:1] + e[-1:]} for e in edges]
        for line in sorted(set.intersection(*per_page)):
            add("info", "repeated_line", f"'{line}' appears on every page (header/footer?). Usually harmless, "
                "but some parsers fold it into the surrounding section.")

    return {"pdf": str(pdf), "pages": [{"page": i, "chars": len(t)} for i, t in enumerate(pages, 1)],
            "experience_years": years, "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", nargs="?", type=Path, default=HERE / "output" / "default.pdf")
    parser.add_argument("--content", type=Path, help="content JSON (default: content/<pdf name>.json if present)")
    parser.add_argument("--out", type=Path, help="JSON report path (default: analysis/<pdf name>.pdf-check.json)")
    parser.add_argument("--no-network", action="store_true", help="skip opening the LinkedIn/GitHub/website links")
    args = parser.parse_args()

    content_path = args.content or HERE / "content" / f"{args.pdf.stem}.json"
    content = json.loads(content_path.read_text(encoding="utf-8")) if content_path.exists() else None
    report = check(args.pdf, content, template_headings(TEMPLATE), network=not args.no_network)
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
