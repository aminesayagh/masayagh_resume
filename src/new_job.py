#!/usr/bin/env python3
"""Scaffold a new job application folder from a posting.

Usage: python3 src/new_job.py --url JOB_URL
       python3 src/new_job.py --from jobs/<slug>     # next version of a job: its tailoring, with the latest experience lines
       python3 src/new_job.py [--company NAME] [--title TITLE] [--posting FILE]

--url reads the title, company, description and location from the posting page
(src/fetch_posting.py); --company/--title override what it found.

Prompts for the posting text when not given (paste it, then press Ctrl-D). src/parse_offer.py (one Haiku call,
cached) reads the company, title, location and the skills the posting asks for, each with its type, priority and
minimum years; --company/--title and --url win over what it found. Refuses to run if template/content/default.json
has any unresolved spelling, style or PDF-readability finding: every new application starts from that baseline.
Creates jobs/<company>-<title>-v<N>/, its offer and requirements in data/resume.db (a new skill is saved unconfirmed,
for you to review or merge), composes the experience lines for the offer, builds the resume and writes the review.
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
import db
import offers
import paths
import check_template
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


COPIED = ("content/content.json", "content/cover.json", "content/cover-fr.json")  # the offer is copied in the db


def new_version(source: Path) -> Path:
    """Copy a job (typically a sent, frozen one) into its next -vN folder, ready to edit. Summary, title, skills and
    cover letters are copied; the experience lines are composed again from the library (db -> json), so the new
    version gets the latest approved wording. The source folder is never changed."""
    source = source.resolve()
    base = re.sub(r"-v\d+$", "", source.name)
    folder = JOBS_DIR / f"{base}-v{next_version(base)}"
    folder.mkdir()
    for name in COPIED:
        if (source / name).exists():
            (folder / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, folder / name)
    job = offers.load(source)
    job.pop("sent", None)
    job.pop("template_sha", None)  # tailored content, not a template copy
    has_requirements = bool(job.pop("requirements", None))  # they stay on the offer, shared via job["offer_id"]
    offers.save(folder, job)
    print(f"Created {folder.relative_to(ROOT)} from {source.name} (not sent; edit, then run src/tailor.py).")
    if has_requirements:
        import compose  # late: compose imports build_resume, like this module
        compose.compose(folder)
    else:
        print("No requirements yet: experience lines kept as in the previous version; draft them, then compose.")
    build_resume.build(paths.content(folder))
    return folder


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--from":
        new_version(Path(sys.argv[2]))
        return
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
        print("template/content/default.json has unresolved findings; fix those before starting a new job\n"
              "(or run src/check_template.py on its own to see this list anytime):\n")
        for f in problems:
            print(f"[{f['severity']}] {f['message']}")
        sys.exit(1)

    if found:
        posting = f"Source: {found['url']}\nLocation: {found['location']}\n\n{found['description']}"
    elif args.posting:
        posting = args.posting.read_text(encoding="utf-8").strip()
    else:
        print("Paste the job posting, then press Ctrl-D:")
        posting = sys.stdin.read().strip()
    try:
        import parse_offer  # late: it needs the claude CLI only when a posting is parsed
        parsed = parse_offer.parse(posting)
    except Exception as exc:  # no claude CLI, no login, a timeout: the job is still created, without requirements
        print(f"[warning] the posting could not be parsed ({exc}); the job is created without requirements.")
        parsed = {}
    company = (args.company or found.get("company") or parsed.get("company") or input("Company: ")).strip()
    title = (args.title or found.get("title") or parsed.get("title") or input("Job title: ")).strip()
    if not company or not title or not posting:
        sys.exit("Company, job title and posting text are all required.")

    slug = f"{slugify(company)}-{slugify(title)}"
    folder = JOBS_DIR / f"{slug}-v{next_version(slug)}"
    folder.mkdir(parents=True)

    content_path = paths.content(folder)
    content_path.parent.mkdir(parents=True, exist_ok=True)
    paths.review_md(folder).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE_DIR / "content" / "default.json", content_path)
    name = json.loads(content_path.read_text(encoding="utf-8"))["name"]
    job = {"title": f"{company} — {title}", "posting_text": posting,
           "pdf_name": pdf_name(name, title, company),
           "company": slugify(company),
           **({"url": found["url"]} if found else {}),
           "location": (found or {}).get("location") or offers.parsed_location(parsed),
           "template_sha": hashlib.sha256(content_path.read_bytes()).hexdigest(),
           "requirements": offers.from_parsed(parsed)}
    job_path = paths.job(folder)
    offers.save(folder, job)  # the offer, its requirements and this composition live in data/resume.db
    job = offers.load(folder)  # one requirement per keyword, as the review reads it
    if job["requirements"]:
        import compose  # late: compose imports build_resume, like this module
        compose.compose(folder)

    pdf_path = build_resume.build(content_path)
    content = json.loads(content_path.read_text(encoding="utf-8"))
    rep = review_ats.review(job, pdf_path, content, network=False)
    inputs = {"cv": review_ats.rel(pdf_path), "job": review_ats.rel(job_path), "content": review_ats.rel(content_path)}
    paths.review_md(folder).write_text(review_ats.markdown(rep, inputs), encoding="utf-8")
    rep["pdf_check"]["pdf"] = inputs["cv"]
    paths.review_json(folder).write_text(json.dumps({**inputs, **rep}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nCreated {folder}")
    if rep.get("job_title") and not rep["job_title"]["match"]:
        print(f"[warning] {rep['job_title']['message']}")
    publish_resume.publish(job_path)
    new = db.connect().execute("SELECT count(*) FROM skills WHERE confirmed = 0").fetchone()[0]
    print(f"{len(job['requirements'])} requirement(s) saved from the posting; {new} skill(s) to confirm or merge.")
    print(f"Next: review the gaps and tailor: .venv/bin/python src/tailor.py jobs/{folder.name}")


assert pdf_name("Mohamed Amine Sayagh", "Développeur Full-Stack", "theodo") == "Mohamed-Amine-Sayagh-Developpeur-Full-Stack-Theodo.pdf"

if __name__ == "__main__":
    main()
