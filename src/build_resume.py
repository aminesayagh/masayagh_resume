#!/usr/bin/env python3
"""Build a tailored PDF resume from a JSON content file.

Usage: python3 src/build_resume.py [template/default.json] [-o path/to/resume.pdf]
Requires Jinja2 and Google Chrome in WSL.
"""

import argparse
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
DEFAULT_DATA = TEMPLATE_DIR / "default.json"
MAX_PAGES = 3  # the user's limit; going over warns, it doesn't fail
SKILL_ROWS = 6  # languages, 3 rows of development technologies, design tools, AI


def skills_problem(skills: list) -> str | None:
    """The user's limit: 6 rows, and as many skills per row as template/default.json."""
    template = [len(r) for r in json.loads(DEFAULT_DATA.read_text(encoding="utf-8"))["skills"]]
    shape = [len(r) for r in skills]
    if len(shape) != SKILL_ROWS:
        return f"skills have {len(shape)} rows; the layout is {SKILL_ROWS} (languages, 3x development, design, AI)"
    if shape != template:
        return f"skills per row are {shape}; the template's are {template}. Replace skills, don't add or remove"
    return None
sys.path.insert(0, str(HERE / "vendor"))
sys.dont_write_bytecode = True
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
    """<folder>/<job.json's pdf_name> for a job folder, else <folder>/resume.pdf."""
    folder = data_path.resolve().parent
    job_file = folder / "job.json"
    name = json.loads(job_file.read_text(encoding="utf-8")).get("pdf_name") if job_file.exists() else None
    return folder / (name or "resume.pdf")


def mark_readiness(data_path: Path, pdf_file: Path, output_path: Path | None, ready: bool) -> Path:
    """A job PDF that is not ready to send (over 3 pages, broken skills layout) is renamed with a leading '_'
    and the ready-named file is removed, so a not-ready resume can't be attached or published by mistake."""
    if output_path is not None or not (data_path.resolve().parent / "job.json").exists():
        return pdf_file
    draft = pdf_file.with_name("_" + pdf_file.name)
    if ready:
        draft.unlink(missing_ok=True)
        return pdf_file
    shutil.move(str(pdf_file), draft)
    print(f"NOT READY TO SEND: saved as {draft.name}; fix the warnings above, then rebuild.")
    return draft


def refresh_job_report(data_path: Path, pdf_file: Path, output_path: Path | None) -> None:
    """A job's own PDF changed: re-run its review so report, interview prep and dashboard match it.
    Skipped for the template, for -o builds elsewhere, and before requirements are drafted."""
    job_file = data_path.resolve().parent / "job.json"
    if output_path is not None or not job_file.exists():
        return
    job = json.loads(job_file.read_text(encoding="utf-8"))
    if not job.get("requirements"):
        return
    import check_job, review_ats  # late: review_ats is heavier and not needed for template builds
    if [f for f in check_job.validate(job, ROOT, draft=True) if f["severity"] == "error"]:
        print("Job file has errors; report not refreshed (run src/check_job.py).")
        return
    review_ats.refresh(job_file, job, pdf_file, data_path.resolve())


def build(data_path: Path, output_path: Path | None = None) -> Path:
    """Render and print `data_path` to PDF. Returns the PDF path."""
    data = load_data(data_path.resolve(strict=True))
    qr_url = data["contact"].get("qr_url") or data["contact"]["website_link"]
    data["contact"]["qr_url"] = qr_url
    pdf_file = (output_path or default_pdf(data_path)).resolve()
    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    browser = shutil.which("google-chrome")
    if browser is None:
        raise RuntimeError("Google Chrome is unavailable in WSL")
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
    )
    with tempfile.TemporaryDirectory(prefix="resume-build-") as temporary:
        temporary_dir = Path(temporary)
        html_file = temporary_dir / "resume.html"
        rendered_pdf = temporary_dir / "resume.pdf"
        html_file.write_text(
            env.get_template("resume.html").render(
                data=data,
                experience_date_parts=experience_date_parts,
                qr_svg=qr_svg(qr_url),
                font_base=(TEMPLATE_DIR / "fonts").resolve().as_uri() + "/",
                asset_base=(TEMPLATE_DIR / "assets").resolve().as_uri() + "/",
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
        page_count = match.group(1)
    print(f"Created {pdf_file} ({page_count} pages)")
    problem = skills_problem(data["skills"])
    if problem:
        print(f"WARNING: {problem}.")
    if int(page_count) > MAX_PAGES:
        from pypdf import PdfReader
        spill = " ".join(PdfReader(pdf_file).pages[-1].extract_text().split())[:160]
        print(f"WARNING: over {MAX_PAGES} pages. Last page starts with: {spill}")
    pdf_file = mark_readiness(data_path, pdf_file, output_path, int(page_count) <= MAX_PAGES and not problem)
    refresh_job_report(data_path, pdf_file, output_path)
    if output_path is None and (data_path.resolve().parent / "job.json").exists():
        import build_cover  # late: imports this module
        build_cover.build(data_path.resolve().parent)
    return pdf_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", type=Path, default=DEFAULT_DATA,
                        help="JSON file for this job application (default: template/default.json)")
    parser.add_argument("-o", "--output", type=Path,
                        help="PDF path (default: job.json's pdf_name in the JSON file's folder, else resume.pdf)")
    args = parser.parse_args()
    build(args.data, args.output)


if __name__ == "__main__":
    main()
