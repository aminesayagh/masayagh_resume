#!/usr/bin/env python3
"""Build jobs/<slug>/dashboard.html: one page with everything known about one job offer.

Usage: python3 src/dashboard.py [jobs/<slug> ...]   (no argument: every job folder)

Reads the folder's job.json, review.json, interview.json and posting.txt and writes a
static page: location check, links, evidence coverage, requirements with the resume
lines that back them, interview prep topics and the full posting. Nothing is computed here that the other tools don't already
write; rerun it after src/review_ats.py or src/new_job.py (both call it).
"""

import json
from datetime import datetime
from html import escape
from pathlib import Path

import skills_inventory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
JOBS = ROOT / "jobs"
SITE = "https://www.masayagh.com"

CSS = """
body{font:14px/1.5 system-ui,sans-serif;color:#0f1828;background:#f6f7f9;margin:0;padding:24px;max-width:1200px;margin:auto}
h1{font-size:22px;margin:0 0 4px} h2{font-size:18px;margin:0} h3{font-size:15px;margin:18px 0 6px}
.muted{color:#667085} .card{background:#fff;border:1px solid #e4e7ec;border-radius:10px;padding:16px 20px;margin:16px 0}
table{border-collapse:collapse;width:100%;background:#fff} th,td{border-bottom:1px solid #eaecf0;padding:6px 8px;text-align:left;vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:#667085}
.tag{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.met{background:#dcfae6;color:#067647} .partial{background:#fef0c7;color:#b54708} .missing,.uncertain{background:#fee4e2;color:#b42318}
.prepare_story{background:#dcfae6;color:#067647} .prove_claim{background:#fef0c7;color:#b54708} .gap{background:#fee4e2;color:#b42318}
.same{background:#dcfae6;color:#067647} .other{background:#fef0c7;color:#b54708}
summary{cursor:pointer;font-weight:600} pre{white-space:pre-wrap;font:13px/1.5 system-ui,sans-serif;background:#f9fafb;padding:12px;border-radius:8px}
.quote{color:#475467;font-style:italic} a{color:#1849a9}
"""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def tag(text: str, cls: str | None = None) -> str:
    return f'<span class="tag {escape(cls or text)}">{escape(text)}</span>'


def location_tag(verdict: str) -> str:
    if not verdict:
        return '<span class="muted">not checked</span>'
    return tag(verdict, "same" if verdict.startswith(("same", "remote, listed in same")) else "other")


def coverage(review: dict) -> str:
    cov = review.get("evidence_coverage")
    if not cov or cov.get("must_have") is None:
        return '<span class="muted">no requirements reviewed yet</span>'
    return f"must-have <b>{cov['must_have']}</b> · preferred <b>{cov['preferred']}</b>"


def job_card(folder: Path, job: dict, review: dict, prep: dict) -> str:
    url, pdf = job.get("url"), job.get("pdf_name")
    published = f"{SITE}/resume/{job['company']}/{pdf}" if job.get("company") and pdf else None
    pdf_check = review.get("pdf_check", {})
    errors = sum(f["severity"] == "error" for f in pdf_check.get("findings", []))
    warnings = sum(f["severity"] == "warning" for f in pdf_check.get("findings", []))
    links = " · ".join(x for x in (
        f'<a href="{escape(url)}">job posting</a>' if url else "",
        f'<a href="{escape(published)}">published resume</a>' if published else "",
        f'<a href="{escape(pdf)}">local PDF (ready to send)</a>' if pdf and (folder / pdf).exists() else
        f'<a href="_{escape(pdf)}">local PDF: NOT READY, do not send</a>' if pdf and (folder / f"_{pdf}").exists() else "",
        f'<a href="review.md">review.md</a>' if (folder / "review.md").exists() else "") if x)
    unreviewed = review.get("unreviewed", 0)
    parts = [f'<div class="card" id="{escape(folder.name)}"><h2>{escape(job.get("title", folder.name))}</h2>',
             f"<p>{tag('draft', 'partial')} {unreviewed} requirement(s) not reviewed yet; quotes and priorities may change.</p>"
             if unreviewed else "",
             f'<p class="muted">{escape(folder.name)} · {links}</p>',
             (f"<p><b>Job title:</b> {tag('warning', 'missing')} {escape(review['job_title']['message'])}</p>"
              if review.get("job_title") and not review["job_title"]["match"] else
              f"<p><b>Job title:</b> {tag('matches', 'met')} {escape(review['job_title']['posting'])}</p>" if review.get("job_title") else ""),
             f"<p><b>Location:</b> {escape(job.get('location') or 'not recorded')} {location_tag(job.get('location_match', ''))}<br>",
             f"<b>Evidence coverage:</b> {coverage(review)} "
             f"<span class='muted'>((met + 0.5 × partial) ÷ requirements, per priority; not an ATS score)</span><br>",
             f"<b>PDF:</b> {len(pdf_check.get('pages', []))} pages, {errors} errors, {warnings} warnings · "
             f"<b>Spelling:</b> {len(review.get('spelling', {}).get('findings', []))} warnings</p>"]

    results = review.get("results") or []
    posting_quote = {q["id"]: q.get("quote", "") for q in job.get("requirements", [])}  # results hold PDF lines, not these
    if results:
        rows = "".join(
            f"<tr><td>{escape(r['id'])}</td><td>{escape(r['priority'].replace('_', '-'))}</td><td>{tag(r['status'])}</td>"
            f"<td>{escape(r.get('description') or '')}<div class='quote'>“{escape(posting_quote.get(r['id'], ''))}”</div></td>"
            f"<td>{'<br>'.join(f'{escape(t['term'])} {tag(t['status'])}' for t in r.get('terms', []))}</td>"
            f"<td>{'<br>'.join(escape(t['quote']) for t in r.get('terms', []) if t.get('quote')) or '<span class=muted>none</span>'}</td></tr>"
            for r in results)
        parts.append(f"<h3>Requirements</h3><table><tr><th>Id</th><th>Priority</th><th>Status</th>"
                     f"<th>Requirement · posting quote</th><th>Terms</th><th>Resume line found</th></tr>{rows}</table>")
    else:
        parts.append('<p class="muted">No requirements drafted yet: ask for them to be drafted from posting.txt.</p>')

    gaps = [(r["id"], t["term"], r["targets"], t["found_in"], t["missing_from"]) for r in results if r.get("targets")
            for t in r.get("terms", []) if t.get("missing_from")]
    if gaps:
        rows = "".join(f"<tr><td>{escape(i)}</td><td>{escape(term)}</td><td>{escape(', '.join(want))}</td>"
                       f"<td>{escape(', '.join(found)) or '-'}</td><td>{tag(', '.join(miss), 'missing')}</td></tr>"
                       for i, term, want, found, miss in gaps)
        parts.append(f"<h3>Placement gaps</h3><table><tr><th>Id</th><th>Term</th><th>Wanted in</th><th>Found in</th>"
                     f"<th>Missing from</th></tr>{rows}</table>")

    if prep.get("topics"):
        rows = "".join(
            f"<tr><td>{escape(t['id'])}</td><td>{tag(t['focus'])}</td><td>{escape(t['requirement'])}</td>"
            f"<td>{'<br>'.join(escape(q) for q in t['your_resume_says']) or '<span class=muted>nothing yet</span>'}</td>"
            f"<td>{escape(', '.join(t['terms_not_met']))}</td></tr>" for t in prep["topics"])
        hints = "".join(f"<li>{tag(k)} {escape(v)}</li>" for k, v in prep.get("how_to_prepare", {}).items() if k != "source")
        parts.append(f"<h3>Interview prep</h3><ul>{hints}</ul><p class='muted'>{escape(prep['how_to_prepare'].get('source', ''))}</p>"
                     f"<table><tr><th>Id</th><th>Focus</th><th>Requirement</th><th>Your resume says</th><th>Terms not met</th></tr>{rows}</table>")

    content_file = folder / "content.json"
    if content_file.exists():
        skills = skills_inventory.job_skills(job, json.loads(content_file.read_text(encoding="utf-8")))
        rows = "".join(f"<tr><td>{escape(k['name'])}</td><td>{escape(skills_inventory.label(k['years']))}</td>"
                       f"<td>{tag('asked', 'met') if k['in_job'] else ''}</td></tr>" for k in skills)
        paste = ", ".join(f"{k['name']}: {skills_inventory.label(k['years'])}" for k in skills if k["years"] is not None)
        missing = [k["name"] for k in skills if k["years"] is None]
        parts.append(f"<h3>Skills for application forms</h3><p class='muted'>Years from template/skills.json "
                     f"(start date to today). 'asked' = the posting asks for it.</p>"
                     f"<textarea readonly rows='4' style='width:100%'>{escape(paste)}</textarea>"
                     + (f"<p>{tag('start date needed', 'missing')} {escape(', '.join(missing))}</p>" if missing else "")
                     + f"<table><tr><th>Skill</th><th>Experience</th><th>In posting</th></tr>{rows}</table>")

    posting = folder / "posting.txt"
    if posting.exists():
        parts.append(f"<details><summary>Full job posting</summary><pre>{escape(posting.read_text(encoding='utf-8'))}</pre></details>")
    return "".join(parts) + "</div>"


def build(folder: Path) -> Path:
    job = load(folder / "job.json")
    card = job_card(folder, job, load(folder / "review.json"), load(folder / "interview.json"))
    title = escape(job.get("title", folder.name))
    out = folder / "dashboard.html"
    out.write_text(f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style>"
                   f"</head><body><p class='muted'>Built {datetime.now():%Y-%m-%d %H:%M} from {escape(folder.name)}/. "
                   f"Coverage shows how much of the posting the resume text backs up; it is not an ATS score or a "
                   f"hiring prediction.</p>{card}</body></html>", encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    folders = [Path(a) for a in sys.argv[1:]] or sorted(p.parent for p in JOBS.glob("*/job.json"))
    for folder in folders:
        print(f"Dashboard: {build(folder)}")
