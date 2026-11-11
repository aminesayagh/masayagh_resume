"""Read-only view of jobs/: one summary per job, search and filters, and the cross-job skills view.

Nothing here writes to jobs/ or template/; changes go through the scripts in src/ (see app.py).
"""

import json
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def status(folder: Path, job: dict, review: dict) -> str:
    """sent > not ready (a '_' resume) > no requirements > draft (unreviewed) > ready."""
    pdf = job.get("pdf_name", "resume.pdf")
    if job.get("sent"):
        return "sent"
    if (folder / f"_{pdf}").exists():
        return "not ready"
    if not job.get("requirements"):
        return "no requirements"
    if any(not r.get("reviewed") for r in job["requirements"]):
        return "draft"
    return "ready"


def summary(folder: Path) -> dict:
    job, review = load(folder / "job.json"), load(folder / "review.json")
    company, _, title = job.get("title", folder.name).partition(" — ")
    cov = review.get("evidence_coverage") or {}
    posting = folder / "posting.txt"
    return {
        "slug": folder.name, "company": company, "title": title or company, "status": status(folder, job, review),
        "sent": job.get("sent"), "location": job.get("location", ""), "location_match": job.get("location_match", ""),
        "must_have": cov.get("must_have"), "preferred": cov.get("preferred"), "french": bool(job.get("french_version")),
        "created": posting.stat().st_mtime if posting.exists() else 0,
        "terms": sorted({t for r in job.get("requirements", []) for t in r.get("terms", [])}, key=str.casefold),
        "posting": posting.read_text(encoding="utf-8") if posting.exists() else "",
    }


def all_jobs() -> list[dict]:
    return sorted((summary(p.parent) for p in JOBS.glob("*/job.json")), key=lambda j: -j["created"])


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
    for path in JOBS.glob("*/review.json"):
        for r in load(path).get("results", []):
            for t in r.get("terms", []):
                key = (t["term"].casefold(), path.parent.name)
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
    """PDFs grouped by language: the French version's files carry -FR in their name."""
    groups = {"English": [], "French": []}
    for p in sorted(folder.glob("*.pdf")):
        groups["French" if "-FR" in p.stem else "English"].append(p.name)
    for archive in sorted(folder.glob("sent-*/")):  # copies kept by reopen()
        groups[f"As sent on {archive.name[5:]}"] = [f"{archive.name}/{p.name}" for p in sorted(archive.glob("*.pdf"))]
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
    """The user's choice to edit a sent job again: archive every file as sent into sent-<date>/, then drop "sent"."""
    job_file = folder / "job.json"
    job = json.loads(job_file.read_text(encoding="utf-8"))
    archive = folder / f"sent-{job['sent']}"
    archive.mkdir(exist_ok=True)
    for f in folder.iterdir():
        if f.is_file():
            shutil.copy2(f, archive / f.name)
    job.pop("sent")
    job_file.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return archive
