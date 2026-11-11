#!/usr/bin/env python3
"""Build a job's cover letter PDF and the combined resume + cover letter PDF.

Usage: python3 src/build_cover.py jobs/<slug>

Reads jobs/<slug>/cover.json. If it doesn't exist yet, creates it from template/default-cover.json,
filling {company} and {job_title} from job.json. An empty "date" prints today's date.
Writes next to the resume (job.json's pdf_name = <stem>.pdf):
  <stem>-Cover-Letter.pdf             the cover letter alone (one page)
  <stem>-Resume-and-Cover-Letter.pdf  the resume pages, then the cover letter page
A cover letter over one page is saved with a leading '_' (not ready to send), like the resume.
build_resume.py runs this after every job resume build; run it alone after editing cover.json.
"""

import datetime
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from pypdf import PdfReader, PdfWriter

import build_resume

TEMPLATE_DIR = build_resume.TEMPLATE_DIR
DEFAULT_COVER = TEMPLATE_DIR / "default-cover.json"
FR_MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
             "septembre", "octobre", "novembre", "décembre"]


def today(lang: str, day: datetime.date | None = None) -> str:
    day = day or datetime.date.today()
    if lang == "fr":
        return f"{day.day} {FR_MONTHS[day.month - 1]} {day.year}"
    return f"{day:%B} {day.day}, {day.year}"


def company_and_title(job: dict) -> tuple[str, str]:
    """new_job.py writes title as 'Company — Job title'."""
    company, _, title = job["title"].partition(" — ")
    return (company, title) if title else (job.get("company", ""), job["title"])


def ensure_cover(folder: Path, job: dict) -> Path:
    path = folder / "cover.json"
    if not path.exists():
        company, title = company_and_title(job)
        text = DEFAULT_COVER.read_text(encoding="utf-8")
        # json.dumps(...)[1:-1] escapes quotes/backslashes so the result stays valid JSON
        text = text.replace("{company}", json.dumps(company)[1:-1]).replace("{job_title}", json.dumps(title)[1:-1])
        path.write_text(text, encoding="utf-8")
        print(f"Created {path} from {DEFAULT_COVER.name}")
    return path


def load_letter(path: Path) -> dict:
    letter = json.loads(path.read_text(encoding="utf-8"))
    for field in ("company", "job_title", "greeting", "paragraphs"):
        if not letter.get(field):
            raise ValueError(f"{path}: missing {field}")
    leftover = [k for k, v in letter.items() if "{" in json.dumps(v)]
    if leftover:
        raise ValueError(f"{path}: unfilled placeholder in {', '.join(leftover)}")
    letter["date"] = letter.get("date") or today(letter.get("lang", "en"))
    return letter


def render_pdf(data: dict, letter: dict, pdf_file: Path) -> int:
    """Print the letter to pdf_file; returns its page count."""
    browser = shutil.which("google-chrome")
    if browser is None:
        raise RuntimeError("Google Chrome is unavailable in WSL")
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html"]),
                      undefined=StrictUndefined)
    with tempfile.TemporaryDirectory(prefix="cover-build-") as temporary:
        temporary_dir = Path(temporary)
        html_file = temporary_dir / "cover-letter.html"
        html_file.write_text(env.get_template("cover-letter.html").render(
            data=data, letter=letter,
            font_base=(TEMPLATE_DIR / "fonts").resolve().as_uri() + "/",
            asset_base=(TEMPLATE_DIR / "assets").resolve().as_uri() + "/",
        ), encoding="utf-8")
        rendered = temporary_dir / "cover.pdf"
        command = build_resume.chrome_command(browser, str(temporary_dir / "chrome-profile"), html_file)
        subprocess.run(command[:-1] + [f"--print-to-pdf={rendered}", command[-1]], check=True, capture_output=True)
        if not rendered.is_file() or rendered.stat().st_size == 0:
            raise RuntimeError("Chrome did not create the cover letter PDF")
        shutil.move(str(rendered), pdf_file)
    return len(PdfReader(pdf_file).pages)


def settle(path: Path, ready: bool) -> Path:
    """Same convention as build_resume.mark_readiness: a not-ready PDF moves to '_<name>'; the stale twin goes."""
    draft = path.with_name("_" + path.name)
    if ready:
        draft.unlink(missing_ok=True)
        return path
    shutil.move(str(path), draft)
    return draft


def build(folder: Path) -> tuple[Path, Path]:
    folder = folder.resolve()
    job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
    letter = load_letter(ensure_cover(folder, job))
    data = json.loads((folder / "content.json").read_text(encoding="utf-8"))
    stem = Path(job["pdf_name"]).stem

    cover_pdf = folder / f"{stem}-Cover-Letter.pdf"
    pages = render_pdf(data, letter, cover_pdf)
    cover_ready = pages == 1
    if not cover_ready:
        print(f"WARNING: the cover letter is {pages} pages; shorten cover.json's paragraphs to fit one page.")
    final_cover = settle(cover_pdf, cover_ready)

    resume = folder / job["pdf_name"]
    resume_ready = resume.exists()
    if not resume_ready:
        resume = resume.with_name("_" + resume.name)  # build_resume marked it not ready
    combined = folder / f"{stem}-Resume-and-Cover-Letter.pdf"
    writer = PdfWriter()
    for part in (resume, final_cover):
        writer.append(str(part))
    with combined.open("wb") as out:
        writer.write(out)
    combined = settle(combined, resume_ready and cover_ready)
    print(f"Created {final_cover.name} and {combined.name}")
    if not resume_ready:
        print("NOT READY TO SEND: the combined PDF uses a resume that is not ready (see build_resume warnings).")
    return final_cover, combined


assert today("fr", datetime.date(2026, 8, 3)) == "3 août 2026"
assert today("en", datetime.date(2026, 11, 11)) == "November 11, 2026"
assert company_and_title({"title": "Y Strategie — Senior Front-End Developer"}) == ("Y Strategie", "Senior Front-End Developer")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]))
