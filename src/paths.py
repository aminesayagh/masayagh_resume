"""Where everything lives inside a job folder. The only module that knows the layout:

jobs/<slug>/            (the offer itself: posting, details, requirements, is in data/resume.db)
  content/   content.json, content-fr.json, cover.json, cover-fr.json, translate-fr.json
  pdf/       <name>.pdf, <name>-Cover-Letter.pdf, <name>-Resume-and-Cover-Letter.pdf;  pdf/fr/ the -FR files
  review/    review.md, review.json, interview.json, build.json
  history/   sent-<date>/ (exact copies kept when a sent job is reopened)
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"


def job_folder(path: Path) -> Path | None:
    """The job folder that holds `path` (a folder, or a file somewhere inside it), or None outside jobs/."""
    path = path.resolve()
    for candidate in (path, *path.parents):
        if candidate.parent == JOBS.resolve() and candidate.is_dir():
            return candidate
    return None


def job(folder: Path) -> Path:
    """The job's address as scripts pass it around (jobs/<slug>/job.json). The offer itself is in data/resume.db
    (src/offers.py); no such file exists."""
    return folder / "job.json"


def folder_arg(arg: Path) -> Path:
    """A command-line job argument: jobs/<slug> or the old jobs/<slug>/job.json."""
    return arg.parent if arg.name == "job.json" else arg


def content(folder: Path, lang: str = "en") -> Path:
    return folder / "content" / ("content-fr.json" if lang == "fr" else "content.json")


def cover(folder: Path, lang: str = "en") -> Path:
    return folder / "content" / ("cover-fr.json" if lang == "fr" else "cover.json")


def translate_fr(folder: Path) -> Path:
    return folder / "content" / "translate-fr.json"


def review_md(folder: Path) -> Path:
    return folder / "review" / "review.md"


def review_json(folder: Path) -> Path:
    return folder / "review" / "review.json"


def build_json(folder: Path) -> Path:
    """The last build's warnings per part (resume, cover, resume-fr, cover-fr); review.json is rewritten by every review."""
    return folder / "review" / "build.json"


def interview(folder: Path) -> Path:
    return folder / "review" / "interview.json"



def history(folder: Path) -> Path:
    return folder / "history"


def pdf_dir(folder: Path, lang: str = "en") -> Path:
    return folder / "pdf" / ("fr" if lang == "fr" else "")


def stem(folder: Path) -> str:
    """job.json's pdf_name without .pdf ('resume' when unset)."""
    import offers  # late: offers imports this module
    name = offers.load(folder).get("pdf_name") if offers.exists(folder) else None
    return (name or "resume.pdf").removesuffix(".pdf")


def resume_pdf(folder: Path, lang: str = "en") -> Path:
    return pdf_dir(folder, lang) / f"{stem(folder)}{'-FR' if lang == 'fr' else ''}.pdf"


def cover_pdf(folder: Path, lang: str = "en") -> Path:
    return pdf_dir(folder, lang) / f"{stem(folder)}{'-FR' if lang == 'fr' else ''}-Cover-Letter.pdf"


def combined_pdf(folder: Path, lang: str = "en") -> Path:
    return pdf_dir(folder, lang) / f"{stem(folder)}{'-FR' if lang == 'fr' else ''}-Resume-and-Cover-Letter.pdf"


def not_ready(path: Path) -> Path:
    """The '_'-prefixed twin of a PDF that isn't ready to send."""
    return path.with_name("_" + path.name.lstrip("_"))
