#!/usr/bin/env python3
"""Build a job's cover letter PDF and the combined resume + cover letter PDF.

Usage: python3 src/build_cover.py jobs/<slug>

Reads jobs/<slug>/content/cover.json. If it doesn't exist yet, creates it from the default letter in data/resume.db,
filling {company} and {job_title} from the offer. An empty "date" prints today's date.
Writes into jobs/<slug>/pdf/ (the offer's pdf_name = <stem>.pdf; French in pdf/fr/):
  <stem>-Cover-Letter.pdf             the cover letter alone (one page)
  <stem>-Resume-and-Cover-Letter.pdf  the resume pages, then the cover letter page
A cover letter whose text overflows the page is saved with a leading '_' (not ready to send), like the resume.
build_resume.py runs this after every job resume build; run it alone after editing cover.json.
"""

import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from pypdf import PdfWriter

import build_resume
import db
import paths
import offers
import check_style

TEMPLATE_DIR = build_resume.TEMPLATE_DIR


FR_MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
             "septembre", "octobre", "novembre", "décembre"]


def today(day: datetime.date | None = None, lang: str = "en") -> str:
    """English for every application; French only for the local French version (build_fr.py)."""
    day = day or datetime.date.today()
    if lang == "fr":
        return f"{day.day} {FR_MONTHS[day.month - 1]} {day.year}"
    return f"{day:%B} {day.day}, {day.year}"


def company_and_title(job: dict) -> tuple[str, str]:
    """new_job.py writes title as 'Company — Job title'."""
    company, _, title = job["title"].partition(" — ")
    return (company, title) if title else (job.get("company", ""), job["title"])


def default_letter(company: str, title: str, lang: str = "en", con=None) -> dict:
    """The default letter from data/resume.db: the paragraphs marked default_order, greeting and closing in profile."""
    con = con or db.connect()
    fr = lang == "fr"
    words = {k: (f if fr and f is not None else e) for k, e, f in
             con.execute("SELECT key, text_en, text_fr FROM profile WHERE key IN ('cover_greeting', 'cover_closing')")}
    fill = lambda t: t.replace("{company}", company).replace("{job_title}", title)
    return {"date": "", "company": company, "hiring_contact": "", "job_title": title, "reference": "",
            "greeting": words["cover_greeting"],
            "paragraphs": [fill(f if fr and f else e) for e, f in con.execute(
                "SELECT text_en, text_fr FROM cover_paragraphs WHERE default_order IS NOT NULL ORDER BY default_order")],
            "closing": words["cover_closing"]}


def ensure_cover(folder: Path, job: dict) -> Path:
    path = paths.cover(folder)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(default_letter(*company_and_title(job)), indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"Created {path} from the default letter in data/resume.db")
    return path


def load_letter(path: Path, lang: str = "en") -> dict:
    letter = json.loads(path.read_text(encoding="utf-8"))
    for field in ("company", "job_title", "greeting", "paragraphs"):
        if not letter.get(field):
            raise ValueError(f"{path}: missing {field}")
    leftover = [k for k, v in letter.items() if "{" in json.dumps(v)]
    if leftover:
        raise ValueError(f"{path}: unfilled placeholder in {', '.join(leftover)}")
    letter["lang"] = lang
    letter["date"] = letter.get("date") or today(lang=lang)
    return letter


def render_pdf(data: dict, letter: dict, pdf_file: Path) -> bool:
    """Print the letter to pdf_file; returns True when all text fits above the footer.
    The page clips overflow, so the page count can't tell; the template's script sets data-overflow."""
    browser = shutil.which("google-chrome")
    if browser is None:
        raise RuntimeError("Google Chrome is unavailable in WSL")
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR / "layout"), autoescape=select_autoescape(["html"]),
                      undefined=StrictUndefined)
    with tempfile.TemporaryDirectory(prefix="cover-build-") as temporary:
        temporary_dir = Path(temporary)
        html_file = temporary_dir / "cover-letter.html"
        html_file.write_text(env.get_template("cover-letter.html").render(
            data=data, letter=letter,
            font_base=(TEMPLATE_DIR / "layout" / "fonts").resolve().as_uri() + "/",
            asset_base=(TEMPLATE_DIR / "layout" / "assets").resolve().as_uri() + "/",
        ), encoding="utf-8")
        rendered = temporary_dir / "cover.pdf"
        command = build_resume.chrome_command(browser, str(temporary_dir / "chrome-profile"), html_file)
        dom = subprocess.run(command[:-1] + ["--dump-dom", command[-1]], check=True, capture_output=True, text=True).stdout
        match = re.search(r'<body[^>]*data-overflow="(yes|no)"', dom)
        if match is None:
            raise RuntimeError("The browser did not finish laying out the cover letter")
        subprocess.run(command[:-1] + [f"--print-to-pdf={rendered}", command[-1]], check=True, capture_output=True)
        if not rendered.is_file() or rendered.stat().st_size == 0:
            raise RuntimeError("Chrome did not create the cover letter PDF")
        shutil.move(str(rendered), pdf_file)
    return match.group(1) == "no"


def settle(path: Path, ready: bool) -> Path:
    """Same convention as build_resume.mark_readiness: a not-ready PDF moves to '_<name>'; the stale twin goes."""
    draft = paths.not_ready(path)
    if ready:
        draft.unlink(missing_ok=True)
        return path
    shutil.move(str(path), draft)
    return draft


def build(folder: Path, lang: str = "en") -> tuple[Path, Path]:
    """lang="fr": the local French version, from cover-fr.json and content-fr.json, files suffixed -FR."""
    folder = folder.resolve()
    if reason := build_resume.frozen(folder):
        raise SystemExit(reason)
    job = offers.load(folder)
    resume = paths.resume_pdf(folder, lang)
    if lang == "fr":
        letter = load_letter(paths.cover(folder, "fr"), lang="fr")
        data = json.loads(paths.content(folder, "fr").read_text(encoding="utf-8"))
    else:
        letter = load_letter(ensure_cover(folder, job))
        data = json.loads(paths.content(folder).read_text(encoding="utf-8"))
    stem = resume.stem

    cover_pdf = paths.cover_pdf(folder, lang)
    cover_pdf.parent.mkdir(parents=True, exist_ok=True)
    cover_ready = render_pdf(data, letter, cover_pdf)
    warnings = [] if cover_ready else ["the cover letter text runs past the page and is cut off; shorten cover.json's paragraphs."]
    final_cover = settle(cover_pdf, cover_ready)

    resume_ready = resume.exists()
    if not resume_ready:
        resume = paths.not_ready(resume)  # build_resume marked it not ready
    combined = paths.combined_pdf(folder, lang)
    writer = PdfWriter()
    for part in (resume, final_cover):
        writer.append(str(part))
    with combined.open("wb") as out:
        writer.write(out)
    combined = settle(combined, resume_ready and cover_ready)
    print(f"Created {final_cover.name} and {combined.name}")
    for i, paragraph in enumerate(letter["paragraphs"], 1):  # same repetition rules as the resume
        if twice := check_style.repeats(paragraph):
            warnings.append(f"cover letter paragraph {i} repeats {', '.join(repr(w) for w in twice)}; vary the wording.")
    if words := check_style.overused(letter["paragraphs"], min_lines=3):
        warnings.append("same words in 3+ paragraphs: " + ", ".join(f"'{w}' ({n})" for w, n in words.items()))
    if not resume_ready:
        warnings.append("the combined PDF uses a resume that is not ready (see the resume's warnings).")
    for w in warnings:
        print(f"WARNING: {w}")
    build_resume.record_build(folder, "cover" + ("-fr" if lang == "fr" else ""), warnings, cover_ready)
    return final_cover, combined


assert today(datetime.date(2026, 11, 11)) == "November 11, 2026"
assert today(datetime.date(2026, 8, 3), "fr") == "3 août 2026"
assert company_and_title({"title": "Y Strategie — Senior Front-End Developer"}) == ("Y Strategie", "Senior Front-End Developer")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]))
