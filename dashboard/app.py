"""Local job dashboard: browse, search and act on the job folders.

Run from the repo root:  .venv/bin/python -m uvicorn dashboard.app:app --host 127.0.0.1 --port 8000
Reads jobs/ (dashboard/data.py). Changes go through the src/ scripts, so their rules hold: sent jobs are frozen,
'_' marks a resume that is not ready, 3 pages max. The only direct write is "Mark as sent" (one field in job.json).
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from dashboard import data

ROOT = data.ROOT
PYTHON = ROOT / ".venv" / "bin" / "python"
sys.path.insert(0, str(ROOT / "src"))
import job_page  # noqa: E402  (renders one job's details)
import skills_inventory  # noqa: E402

app = FastAPI(title="Job dashboard", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# action -> (label, what it does, allowed?, command)
ACTIONS = {
    "sent": ("Mark as sent", "Freezes this job: no rebuild, edit or republish afterwards.",
             lambda j: not j["sent"], None),
    "reopen": ("Reopen (sent → in progress)",
               "Removes the freeze so you can edit it again. A copy of every file as sent is kept in sent-<date>/ in "
               "this folder. Warning: once you Tailor it, the published link the employer received shows the new version; "
               "use “New version from this job” instead to leave that link untouched.",
               lambda j: bool(j["sent"]), None),
    "tailor": ("Tailor (build + review + publish)", "Rebuilds the PDFs, refreshes the review and publishes the English resume and cover letter.",
               lambda j: not j["sent"], ["src/tailor.py", "jobs/{slug}"]),
    "french": ("Build French version", "Builds the local French resume and cover letter (never published).",
               lambda j: j["french"] and not j["sent"], ["src/build_fr.py", "jobs/{slug}"]),
    "version": ("New version from this job", "Copies this job into its next -vN folder, keeping its tailoring.",
                lambda j: True, ["src/new_job.py", "--from", "jobs/{slug}"]),
}


def job_or_404(slug: str) -> dict:
    folder = data.JOBS / slug
    if "/" in slug or slug.startswith(".") or not (folder / "job.json").exists():
        raise HTTPException(404, "No such job")
    return data.summary(folder)


@app.get("/", response_class=HTMLResponse)
def jobs(request: Request, q: str = "", status: str = "", skill: str = "", location: str = ""):
    everything = data.all_jobs()
    shown = data.search(everything, q, status, skill, location)
    statuses = sorted({j["status"] for j in everything})
    return templates.TemplateResponse(request, "jobs.html", {
        "jobs": shown, "total": len(everything), "q": q, "status": status, "skill": skill, "location": location,
        "statuses": statuses})


@app.get("/job/{slug}", response_class=HTMLResponse)
def job(request: Request, slug: str, rq: str = "", rstatus: str = "", rpriority: str = ""):
    j = job_or_404(slug)
    folder = data.JOBS / slug
    review = data.load(folder / "review.json")
    total = len(review.get("results", []))
    review["results"] = data.filter_requirements(review.get("results", []), rq, rstatus, rpriority)
    card = job_page.job_card(folder, data.load(folder / "job.json"), review,
                             data.load(folder / "interview.json"), files=f"/files/{slug}/")
    pdfs = data.files_by_language(folder)
    actions = {k: v[:2] for k, v in ACTIONS.items() if v[2](j)}
    return templates.TemplateResponse(request, "job.html", {
        "job": j, "card": card, "pdfs": pdfs, "actions": actions, "rq": rq, "rstatus": rstatus,
        "rpriority": rpriority, "shown": len(review["results"]), "total": total})


@app.get("/skills", response_class=HTMLResponse)
def skills(request: Request):
    inventory = skills_inventory.load()
    rows = data.skills_overview()
    for r in rows:
        found = skills_inventory.find(inventory, r["term"])
        r["years"] = skills_inventory.label(skills_inventory.years(found)) if found else "–"
    return templates.TemplateResponse(request, "skills.html", {"rows": rows})


@app.get("/files/{slug}/{name:path}")
def files(slug: str, name: str):
    job_or_404(slug)
    path = data.JOBS / slug / name
    archived = re.fullmatch(r"sent-[\d-]+/[^/]+", name)  # a copy kept by Reopen
    if ("/" in name and not archived) or ".." in name or not path.is_file() or path.suffix not in (".pdf", ".md"):
        raise HTTPException(404, "No such file")
    return FileResponse(path, media_type="application/pdf" if path.suffix == ".pdf" else "text/plain; charset=utf-8")


@app.get("/job/{slug}/confirm/{action}", response_class=HTMLResponse)
def confirm(request: Request, slug: str, action: str):
    j = job_or_404(slug)
    if action not in ACTIONS or not ACTIONS[action][2](j):
        raise HTTPException(400, "Action not available for this job")
    label, what = ACTIONS[action][:2]
    return templates.TemplateResponse(request, "confirm.html", {"job": j, "action": action, "label": label, "what": what})


@app.post("/job/{slug}/run/{action}", response_class=HTMLResponse)
def run(request: Request, slug: str, action: str):
    j = job_or_404(slug)
    if action not in ACTIONS or not ACTIONS[action][2](j):
        raise HTTPException(400, "Action not available for this job")
    if action == "reopen":
        data.reopen(data.JOBS / slug)
        return RedirectResponse(f"/job/{slug}", status_code=303)
    if action == "sent":
        path = data.JOBS / slug / "job.json"
        job_file = json.loads(path.read_text(encoding="utf-8"))
        job_file["sent"] = date.today().isoformat()
        path.write_text(json.dumps(job_file, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        import db_sync  # records the offer as sent, with a snapshot of its results
        db_sync.sync_job(data.JOBS / slug)
        return RedirectResponse(f"/job/{slug}", status_code=303)
    command = [str(PYTHON)] + [part.format(slug=slug) for part in ACTIONS[action][3]]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=900)
    return templates.TemplateResponse(request, "result.html", {
        "job": j, "label": ACTIONS[action][0], "ok": result.returncode == 0,
        "output": result.stdout + result.stderr})
