#!/usr/bin/env python3
"""Scaffold a new job application folder from a posting.

Usage: python3 src/new_job.py --url JOB_URL
       python3 src/new_job.py [--company NAME] [--title TITLE] [--posting FILE]

--url reads the title, company, description and location from the posting page
(src/fetch_posting.py); --company/--title override what it found.

Prompts for anything not given: the company, the job title, and the posting text
(paste it, then press Ctrl-D). Refuses to run if template/default.json has any unresolved spelling, style
or PDF-readability finding — every new application starts from that baseline, so it
must be clean first. Creates jobs/<company>-<title>-v<N>/ with the posting, a job.json
skeleton (no requirements yet), a copy of the default content, the built resume, and a
partial report (no job-matching section until requirements are drafted).
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import build_resume
import check_template
import dashboard
import fetch_posting
import publish_resume
import review_ats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE_DIR = ROOT / "template"
JOBS_DIR = ROOT / "jobs"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def pdf_name(*parts: str) -> str:
    """'Mohamed Amine Sayagh', 'Software Engineer', 'theodo' -> 'Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf'.
    ASCII only: accents and symbols get mangled by some upload forms."""
    text = unicodedata.normalize("NFKD", " ".join(parts)).encode("ascii", "ignore").decode()
    return "-".join(w[:1].upper() + w[1:] for w in re.findall(r"[A-Za-z0-9]+", text)) + ".pdf"


def next_version(slug: str) -> int:
    pattern = re.compile(rf"{re.escape(slug)}-v(\d+)$")
    versions = [int(m.group(1)) for p in JOBS_DIR.glob(f"{slug}-v*") if p.is_dir() and (m := pattern.fullmatch(p.name))]
    return max(versions, default=0) + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--company")
    parser.add_argument("--title")
    parser.add_argument("--posting", type=Path, help="text file with the job posting")
    parser.add_argument("--url", help="job posting URL: fills company, title, posting and location")
    args = parser.parse_args()
    found = fetch_posting.fetch(args.url) if args.url else {}
    if found:
        print(f"Found: {found['title']} at {found['company']}, {found['location'] or 'no location'} ({found['location_match']})")

    problems = check_template.check()
    if problems:
        print("template/default.json has unresolved findings; fix those before starting a new job\n"
              "(or run src/check_template.py on its own to see this list anytime):\n")
        for f in problems:
            print(f"[{f['severity']}] {f['message']}")
        sys.exit(1)

    company = (args.company or found.get("company") or input("Company: ")).strip()
    title = (args.title or found.get("title") or input("Job title: ")).strip()
    if found:
        posting = f"Source: {found['url']}\nLocation: {found['location']}\n\n{found['description']}"
    elif args.posting:
        posting = args.posting.read_text(encoding="utf-8").strip()
    else:
        print("Paste the job posting, then press Ctrl-D:")
        posting = sys.stdin.read().strip()
    if not company or not title or not posting:
        sys.exit("Company, job title and posting text are all required.")

    slug = f"{slugify(company)}-{slugify(title)}"
    folder = JOBS_DIR / f"{slug}-v{next_version(slug)}"
    folder.mkdir(parents=True)

    (folder / "posting.txt").write_text(posting + "\n", encoding="utf-8")
    content_path = folder / "content.json"
    shutil.copyfile(TEMPLATE_DIR / "default.json", content_path)
    name = json.loads(content_path.read_text(encoding="utf-8"))["name"]
    job = {"title": f"{company} — {title}", "posting_file": f"jobs/{folder.name}/posting.txt",
           "pdf_name": pdf_name(name, title, company),
           "company": slugify(company),
           **({"url": found["url"], "location": found["location"], "location_match": found["location_match"]} if found else {}),
           "template_sha": hashlib.sha256(content_path.read_bytes()).hexdigest(),
           "requirements": []}
    job_path = folder / "job.json"
    job_path.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    pdf_path = build_resume.build(content_path)
    content = json.loads(content_path.read_text(encoding="utf-8"))
    rep = review_ats.review(job, pdf_path, content, network=False)
    inputs = {"cv": review_ats.rel(pdf_path), "job": review_ats.rel(job_path), "content": review_ats.rel(content_path)}
    (folder / "review.md").write_text(review_ats.markdown(rep, inputs), encoding="utf-8")
    rep["pdf_check"]["pdf"] = inputs["cv"]
    (folder / "review.json").write_text(json.dumps({**inputs, **rep}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nCreated {folder}")
    if rep.get("job_title") and not rep["job_title"]["match"]:
        print(f"[warning] {rep['job_title']['message']}")
    print(f"Dashboard: {dashboard.build(folder)}")
    publish_resume.publish(job_path)
    print(f"Report so far: PDF readability + spelling + style (no job requirements yet, so no matching).")
    print(f"Next: draft {job_path.relative_to(ROOT)}'s requirements from posting.txt (see "
          f".claude/skills/ats-review/SKILL.md), then rerun:\n"
          f"  .venv/bin/python src/review_ats.py --job {job_path.relative_to(ROOT)}")


assert pdf_name("Mohamed Amine Sayagh", "Développeur Full-Stack", "theodo") == "Mohamed-Amine-Sayagh-Developpeur-Full-Stack-Theodo.pdf"

if __name__ == "__main__":
    main()
