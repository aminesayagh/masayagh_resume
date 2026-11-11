"""Read-only view of jobs/: one summary per job, search and filters, and the cross-job skills view.

Nothing here writes to jobs/ or template/; changes go through the scripts in src/ (see app.py).
"""

import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import offers  # noqa: E402  (the offers in data/resume.db)
import paths  # noqa: E402  (the job folder layout)

JOBS = paths.JOBS


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def status(folder: Path, job: dict, review: dict) -> str:
    """sent > not ready (a '_' resume) > no requirements > draft (unreviewed) > ready."""
    if job.get("sent"):
        return "sent"
    if paths.not_ready(paths.resume_pdf(folder)).exists():
        return "not ready"
    if not job.get("requirements"):
        return "no requirements"
    if any(not r.get("reviewed") for r in job["requirements"]):
        return "draft"
    return "ready"


def summary(folder: Path) -> dict:
    job, review = offers.load(folder), load(paths.review_json(folder))
    company, _, title = job.get("title", folder.name).partition(" — ")
    cov = review.get("evidence_coverage") or {}
    return {
        "slug": folder.name, "company": company, "title": title or company, "status": status(folder, job, review),
        "sent": job.get("sent"), "location": job.get("location", ""), "location_match": job.get("location_match", ""),
        "must_have": cov.get("must_have"), "preferred": cov.get("preferred"), "french": bool(job.get("french_version")),

        "terms": sorted({t for r in job.get("requirements", []) for t in r.get("terms", [])}, key=str.casefold),
        "posting": job.get("posting_text", ""),
    }


def all_jobs() -> list[dict]:
    return [summary(folder) for folder in offers.all_folders()]  # newest first


def search(jobs: list[dict], q: str = "", status_: str = "", skill: str = "", location: str = "") -> list[dict]:
    """q: words in company, title or posting (all must match); skill: a requirement term; location: verdict text."""
    words = q.casefold().split()
    out = []
    for j in jobs:
        text = f"{j['company']} {j['title']} {j['posting']}".casefold()
        if words and not all(w in text for w in words):
            continue
        if status_ and j["status"] != status_:
            continue
        if skill and not any(skill.casefold() == t.casefold() for t in j["terms"]):
            continue
        if location and location.casefold() not in j["location_match"].casefold():
            continue
        out.append(j)
    return out


def skills_overview() -> list[dict]:
    """Every posting term across jobs: how many jobs ask for it and, per job, the best result on your resume."""
    rank = {"met": 2, "partial": 1}
    best: dict[tuple[str, str], tuple[str, str]] = {}  # (term, job) -> (status, spelling)
    for path in JOBS.glob("*/review/review.json"):
        for r in load(path).get("results", []):
            for t in r.get("terms", []):
                key = (t["term"].casefold(), path.parent.parent.name)
                status_ = t["status"] if t["status"] in rank else "missing"
                if rank.get(status_, 0) >= rank.get(best.get(key, ("missing",))[0], 0):
                    best[key] = (status_, t["term"])
    rows: dict[str, dict] = {}
    for (term, _), (status_, spelling) in best.items():
        row = rows.setdefault(term, {"term": spelling, "jobs": 0, "met": 0, "partial": 0, "missing": 0})
        row["jobs"] += 1
        row[status_] += 1
    return sorted(rows.values(), key=lambda r: (-r["jobs"], r["term"].casefold()))


def files_by_language(folder: Path) -> dict[str, list[str]]:
    """PDF paths relative to the job folder: English (pdf/), French (pdf/fr/), and each copy kept by reopen()."""
    rel = lambda p: p.relative_to(folder).as_posix()
    groups = {"English": [rel(p) for p in sorted(paths.pdf_dir(folder).glob("*.pdf"))],
              "French": [rel(p) for p in sorted(paths.pdf_dir(folder, "fr").glob("*.pdf"))]}
    for archive in sorted(paths.history(folder).glob("sent-*/")):
        groups[f"As sent on {archive.name[5:]}"] = [rel(p) for p in sorted(archive.rglob("*.pdf"))]
    return {k: v for k, v in groups.items() if v}


def filter_requirements(results: list[dict], q: str = "", status_: str = "", priority: str = "") -> list[dict]:
    """q: words in the description, posting quote or terms; status_: met/partial/missing; priority: must_have/preferred."""
    words = q.casefold().split()
    out = []
    for r in results:
        text = " ".join([r.get("description") or "", r.get("posting_quote") or "", *(t["term"] for t in r.get("terms", []))])
        if words and not all(w in text.casefold() for w in words):
            continue
        if status_ and r["status"] != status_:
            continue
        if priority and r["priority"] != priority:
            continue
        out.append(r)
    return out


def reopen(folder: Path) -> Path:
    """The user's choice to edit a sent job again: copy everything as sent into history/sent-<date>/ (JSON content,
    PDFs, review, and the offer as offer.json), then drop "sent"."""
    job = offers.load(folder)
    archive = paths.history(folder) / f"sent-{job['sent']}"
    shutil.copytree(folder, archive, ignore=shutil.ignore_patterns("history"), dirs_exist_ok=True)
    (archive / "offer.json").write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    job.pop("sent")
    offers.save(folder, job)
    return archive
