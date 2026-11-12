#!/usr/bin/env python3
"""Build a tailored PDF resume from a JSON content file.

Usage: python3 src/build_resume.py [template/content/default.json] [-o path/to/resume.pdf]
Requires Jinja2 and Google Chrome in WSL.
"""

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # repo root: template/, src/, jobs/
TEMPLATE_DIR = ROOT / "template"
# French is the only second language: content-fr.json sets "lang": "fr" and the template's labels switch.
FR_LABELS = {"Summary": "Profil", "Skills": "Compétences", "Experience": "Expérience", "Projects": "Projets",
             "Education": "Formation", "Certifications": "Certifications", "Languages": "Langues",
             "Resume": "CV", "en": "fr"}
DEFAULT_DATA = TEMPLATE_DIR / "content" / "default.json"
MAX_PAGES = 3  # the user's limit; going over warns, it doesn't fail
SKILL_ROWS = 6  # languages, 3 rows of development technologies, design tools, AI


def skills_problem(skills: list) -> str | None:
    """The user's limit: 6 rows, and as many skills per row as template/content/default.json."""
    template = [len(r) for r in json.loads(DEFAULT_DATA.read_text(encoding="utf-8"))["skills"]]
    shape = [len(r) for r in skills]
    if len(shape) != SKILL_ROWS:
        return f"skills have {len(shape)} rows; the layout is {SKILL_ROWS} (languages, 3x development, design, AI)"
    if shape != template:
        return f"skills per row are {shape}; the template's are {template}. Replace skills, don't add or remove"
    return None
sys.path.insert(0, str(HERE / "vendor"))
sys.dont_write_bytecode = True
import paths  # noqa: E402
import qrcode  # bundled so the resume builds without another installation step


def qr_svg(url: str) -> str:
    if not url.startswith(("https://", "http://")):
        raise ValueError("The QR destination must be an http or https URL")
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    code.add_data(url)
    code.make(fit=True)
    matrix = code.get_matrix()
    size = len(matrix)
    modules = " ".join(
        f"M{x} {y}h1v1h-1z"
        for y, row in enumerate(matrix)
        for x, filled in enumerate(row)
        if filled
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'role="img" aria-label="QR code" shape-rendering="crispEdges">'
        f'<path d="{modules}" fill="#0F1828"/></svg>'
    )


def load_data(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("The JSON root must be an object")
    for field in ("name", "role", "contact", "summary", "skills", "experience", "education", "languages"):
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    for index, job in enumerate(data["experience"], 1):
        for field in ("dates", "company", "detail", "role", "description", "bullets"):
            if field not in job:
                raise ValueError(f"Experience {index} is missing {field}")
    return data


def experience_date_parts(dates: str) -> tuple[str, str]:
    """Split a displayed date range into start and end labels."""
    parts = re.split(r"\s+(?:-|–|—|to)\s+", dates.strip(), maxsplit=1, flags=re.IGNORECASE)
    return (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")


def chrome_command(browser: str, profile: str, html_file: Path) -> list[str]:
    return [
        browser,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        f"--user-data-dir={profile}",
        "--allow-file-access-from-files",
        "--no-pdf-header-footer",
        "--virtual-time-budget=3000",
        html_file.as_uri(),
    ]


def default_pdf(data_path: Path) -> Path:
    """A job's resume PDF (paths.resume_pdf) for a job's content file, else resume.pdf next to the file."""
    folder = paths.job_folder(data_path)
    return paths.resume_pdf(folder) if folder else data_path.resolve().parent / "resume.pdf"


def frozen(folder: Path) -> str | None:
    """A job whose files were sent (its offer has a sent date in data/resume.db) is frozen: nothing may rebuild, translate or
    republish it, so the folder keeps exactly what the employer received. Changes go into a new version folder."""
    import offers  # late: offers imports paths, which this module imports
    sent = offers.load(folder).get("sent") if offers.exists(folder) else None
    return (f"{folder.name} was sent on {sent}; its files are frozen. To change it, start a new version with "
            f"src/new_job.py (it creates the next -vN folder).") if sent else None


def record_build(folder: Path, part: str, warnings: list[str], ready: bool) -> None:
    """Keep a build's warnings in the job's review/build.json, one entry per part, so the dashboard can say why a
    PDF is not ready. Only that part's entry is replaced."""
    path = paths.build_json(folder)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data[part] = {"built": datetime.datetime.now().isoformat(timespec="minutes"), "ready": ready, "warnings": warnings}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def subject(data: dict, job: dict | None) -> str:
    """'Application for <Title> at <Company>' for a job, else the resume's role."""
    company, _, title = (job or {}).get("title", "").partition(" — ")
    if not title:
        return f"{data['name']} - {data['role']}"
    return f"Candidature : {title} chez {company}" if data.get("lang") == "fr" else f"Application for {title} at {company}"


def set_metadata(pdf: Path, data: dict, title: str, subject_: str) -> None:
    """Chrome writes only the HTML <title>, and a merge writes nothing: set every field ATS and email clients show.
    Keywords are the resume's own skills, never extra posting terms. Creator replaces Chrome's browser string."""
    from pypdf import PdfWriter
    writer = PdfWriter(clone_from=pdf)  # reads the whole file first, so writing back to it is safe
    writer.add_metadata({"/Title": title, "/Author": data["name"], "/Subject": subject_, "/Creator": data["name"],
                         "/Producer": data["name"], "/Keywords": ", ".join(s for row in data["skills"] for s in row)})
    with pdf.open("wb") as out:
        writer.write(out)


def mark_readiness(data_path: Path, pdf_file: Path, output_path: Path | None, ready: bool) -> Path:
    """A job PDF that is not ready to send (over 3 pages, broken skills layout) is renamed with a leading '_'
    and the ready-named file is removed, so a not-ready resume can't be attached or published by mistake."""
    if output_path is not None or paths.job_folder(data_path) is None:
        return pdf_file
    draft = paths.not_ready(pdf_file)
    if ready:
        draft.unlink(missing_ok=True)
        return pdf_file
    shutil.move(str(pdf_file), draft)
    print(f"NOT READY TO SEND: saved as {draft.name}; fix the warnings above, then rebuild.")
    return draft


def refresh_job_report(data_path: Path, pdf_file: Path, output_path: Path | None) -> None:
    """A job's own PDF changed: re-run its review so report, interview prep and dashboard match it.
    Skipped for the template, for -o builds elsewhere, and before requirements are drafted."""
    folder = paths.job_folder(data_path)
    import offers
    if output_path is not None or folder is None or not offers.exists(folder):
        return
    job_file = paths.job(folder)
    job = offers.load(folder)
    if not job.get("requirements"):
        return
    import check_job, review_ats  # late: review_ats is heavier and not needed for template builds
    if [f for f in check_job.validate(job, ROOT, draft=True) if f["severity"] == "error"]:
        print("Job file has errors; report not refreshed (run src/check_job.py).")
        return
    review_ats.refresh(job_file, job, pdf_file, data_path.resolve())
    import db_sync  # the offer, its requirements and any new approved lines join data/resume.db
    db_sync.sync_job(job_file.parent)


def build(data_path: Path, output_path: Path | None = None) -> Path:
    """Render and print `data_path` to PDF. Returns the PDF path."""
    if output_path is None and (folder := paths.job_folder(data_path)) and (reason := frozen(folder)):
        raise SystemExit(reason)
    data = load_data(data_path.resolve(strict=True))
    qr_url = data["contact"].get("qr_url") or data["contact"]["website_link"]
    data["contact"]["qr_url"] = qr_url
    pdf_file = (output_path or default_pdf(data_path)).resolve()
    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    browser = shutil.which("google-chrome")
    if browser is None:
        raise RuntimeError("Google Chrome is unavailable in WSL")
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR / "layout"),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
    )
    env.filters["tr"] = (lambda text: FR_LABELS.get(text, text)) if data.get("lang") == "fr" else (lambda text: text)
    with tempfile.TemporaryDirectory(prefix="resume-build-") as temporary:
        temporary_dir = Path(temporary)
        html_file = temporary_dir / "resume.html"
        rendered_pdf = temporary_dir / "resume.pdf"
        html_file.write_text(
            env.get_template("resume.html").render(
                data=data,
                experience_date_parts=experience_date_parts,
                qr_svg=qr_svg(qr_url),
                font_base=(TEMPLATE_DIR / "layout" / "fonts").resolve().as_uri() + "/",
                asset_base=(TEMPLATE_DIR / "layout" / "assets").resolve().as_uri() + "/",
            ),
            encoding="utf-8",
        )
        command = chrome_command(browser, str(temporary_dir / "chrome-profile"), html_file)
        # The DOM check catches entries too large for one page before producing a clipped PDF.
        result = subprocess.run(command[:-1] + ["--dump-dom", command[-1]], check=True, capture_output=True, text=True)
        match = re.search(r'<body[^>]*data-pages="(\d+)"[^>]*data-pagination-errors="([^"]*)"', result.stdout)
        if match is None:
            raise RuntimeError("The browser did not finish paginating the resume")
        if match.group(2):
            raise ValueError(f"Resume content does not fit: {match.group(2)}")
        subprocess.run(command[:-1] + [f"--print-to-pdf={rendered_pdf}", command[-1]], check=True, capture_output=True, text=True)
        if not rendered_pdf.is_file() or rendered_pdf.stat().st_size == 0:
            raise RuntimeError("Chrome did not create the PDF")
        shutil.move(str(rendered_pdf), pdf_file)
        folder = paths.job_folder(data_path)
        import offers  # late: offers imports build_fr, which imports this module
        job = offers.load(folder) if folder and offers.exists(folder) else None
        set_metadata(pdf_file, data, f"{data['name']} - {data['role']}", subject(data, job))
        page_count = match.group(1)
    print(f"Created {pdf_file} ({page_count} pages)")
    warnings = []
    if problem := skills_problem(data["skills"]):
        warnings.append(f"{problem}.")
    if int(page_count) > MAX_PAGES:
        from pypdf import PdfReader
        spill = " ".join(PdfReader(pdf_file).pages[-1].extract_text().split())[:160]
        warnings.append(f"{page_count} pages, over {MAX_PAGES}. Last page starts with: {spill}")
    for w in warnings:
        print(f"WARNING: {w}")
    ready = int(page_count) <= MAX_PAGES and not problem
    pdf_file = mark_readiness(data_path, pdf_file, output_path, ready)
    if output_path is None and (folder := paths.job_folder(data_path)):
        record_build(folder, "resume", warnings, ready)
    refresh_job_report(data_path, pdf_file, output_path)
    if output_path is None and (folder := paths.job_folder(data_path)):
        import build_cover  # late: imports this module
        build_cover.build(folder)
        import offers
        job = offers.load(folder) if offers.exists(folder) else {}
        if job.get("french_version"):
            import build_fr  # the local French version follows every English build
            build_fr.build(folder)
    return pdf_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", type=Path, default=DEFAULT_DATA,
                        help="JSON file for this job application (default: template/content/default.json)")
    parser.add_argument("-o", "--output", type=Path,
                        help="PDF path (default: a job's pdf/<pdf_name>, else resume.pdf next to the JSON file)")
    args = parser.parse_args()
    build(args.data, args.output)


if __name__ == "__main__":
    main()
