"""Local job dashboard: a JSON API under /api plus the built Vue app (dashboard/web/dist) on the same port.

Run from the repo root:  python3 start.py   (or .venv/bin/python -m uvicorn dashboard.app:app --port 8000 after a build)
The app itself only reads: data/resume.db is opened with mode=ro and jobs/ is only read.
The one write action is "New version", which runs src/new_job.py --from (so the script's rules hold: the source folder,
sent or not, is never changed). Every other write action in the UI is shown disabled ("not wired yet"); fixes happen
in Claude.
"""

import json
import re
import sqlite3
import subprocess
import sys
import threading
from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import offers  # noqa: E402  (load/all_folders take a connection: we pass a read-only one)
import paths  # noqa: E402  (only plain path joins: resume_pdf & co. call stem(), which opens a writable db)
import skills_inventory  # noqa: E402  (pure helpers only: job_skills/years/label; its load() opens a writable db)

DB = ROOT / "data" / "resume.db"
PYTHON = ROOT / ".venv" / "bin" / "python"
WRITE_LOCK = threading.Lock()  # one script at a time: two new versions at once would pick the same -vN
DIST = Path(__file__).parent / "web" / "dist"
MAX_PAGES = 3
BUILD_PARTS = {"resume": "Resume", "cover": "Cover letter", "resume-fr": "French resume", "cover-fr": "French cover letter"}

# What to ask Claude for each finding code of the last build (review.json). Unknown codes fall back to a generic ask.
ASK = {
    "job_title": "ask Claude to align the resume title with the posting",
    "field_missing": "ask Claude why the heading is missing from the PDF",
    "meta_author": "ask Claude to set the PDF author",
    "repeated_line": "nothing to do unless a parser misreads it",
    "measurable": "ask Claude for measurable results you truthfully have",
    "repeated_opener": "ask Claude to vary the verbs",
    "experience_years": "nothing to do",
    "date_overlap": "nothing to do unless the dates are wrong",
}


def ro() -> sqlite3.Connection:
    """The only way this app opens the database: read only, never migrated or restored (unlike src/db.connect)."""
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def pdf(folder: Path, job: dict, kind: str = "resume", lang: str = "en") -> Path:
    """The job's PDF of that kind (resume, cover, combined), or its '_' not-ready twin when only that exists.
    Same names as paths.resume_pdf/cover_pdf/combined_pdf, built from the offer we already loaded."""
    suffix = {"resume": "", "cover": "-Cover-Letter", "combined": "-Resume-and-Cover-Letter"}[kind]
    name = (job.get("pdf_name") or "resume.pdf").removesuffix(".pdf") + ("-FR" if lang == "fr" else "") + suffix + ".pdf"
    path = paths.pdf_dir(folder, lang) / name
    twin = paths.not_ready(path)
    return twin if twin.exists() and not path.exists() else path  # neither: the normal name (not built yet)


def build_notes(folder: Path, job: dict, review: dict) -> list[dict]:
    """Warnings and info from the last build, each with what to ask Claude. Text only: the app fixes nothing."""
    notes = []
    if not job.get("requirements"):
        notes.append({"severity": "warning", "text": "No requirements yet", "ask": "ask Claude to draft them"})
    elif review.get("unreviewed"):
        notes.append({"severity": "info", "text": f"{review['unreviewed']} requirements not reviewed",
                      "ask": "ask Claude to review them"})
    # build.json: each built part's warnings, saying WHY a part is not ready. Jobs built before it existed (and sent
    # jobs, never rebuilt) have no file: fall back to the '_' file alone.
    build = load_json(paths.build_json(folder))
    if pdf(folder, job).name.startswith("_") and not (build.get("resume") or {}).get("warnings"):
        notes.append({"severity": "warning", "text": "Resume marked not ready ('_' file)",
                      "ask": "ask Claude to finish and rebuild it"})
    for part, label in BUILD_PARTS.items():
        built = build.get(part) or {}
        ready = built.get("ready", True)
        for warning in built.get("warnings", []):
            notes.append({"severity": "info" if ready else "warning",
                          "text": f"{label}{'' if ready else ' not ready'}: {warning}",
                          "ask": "ask Claude to fix it" + ("" if ready else ", then rebuild")})
    pages = len((review.get("pdf_check") or {}).get("pages", []))
    if pages > MAX_PAGES:
        notes.append({"severity": "warning", "text": f"Resume is {pages} pages (target {MAX_PAGES})",
                      "ask": "ask Claude to trim it"})
    title = review.get("job_title") or {}
    if title and not title.get("match"):
        notes.append({"severity": title.get("severity", "warning"), "text": title["message"], "ask": ASK["job_title"]})
    for part in ("pdf_check", "spelling", "style"):
        for f in (review.get(part) or {}).get("findings", []):
            notes.append({"severity": f["severity"], "text": f["message"],
                          "ask": ASK.get(f.get("code"), "ask Claude about it")})
    if job.get("french_version") and not pdf(folder, job, lang="fr").exists():
        notes.append({"severity": "warning", "text": "Posting is in French: French version needed",
                      "ask": "ask Claude to build it"})
    order = {"error": 0, "warning": 1, "info": 2}
    return sorted(notes, key=lambda n: order.get(n["severity"], 3))


def summary(folder: Path, con: sqlite3.Connection) -> dict:
    job, review = offers.load(folder, con), load_json(paths.review_json(folder))
    company, _, role = job["title"].partition(" — ")
    cov = review.get("evidence_coverage") or {}
    notes = build_notes(folder, job, review)
    version = re.search(r"-v(\d+)$", folder.name)
    return {
        "slug": folder.name, "company": company, "role": role or company, "version": int(version[1]) if version else 1,
        "status": "sent" if job.get("sent") else "in progress", "sent": job.get("sent"),
        "location": job.get("location", ""),
        "has_requirements": bool(job.get("requirements")),
        "must_have": cov.get("must_have"), "preferred": cov.get("preferred"),
        "warnings": sum(n["severity"] in ("error", "warning") for n in notes),
        "notes": notes,
        "terms": sorted({t for r in job.get("requirements", []) for t in r.get("terms", [])}, key=str.casefold),
    }


def all_jobs() -> list[dict]:
    with ro() as con:
        return [summary(folder, con) for folder in offers.all_folders(con)]  # newest first


def cards(jobs: list[dict], today: date | None = None) -> dict:
    """The four summary cards of the jobs list, from real data only (None = nothing to average)."""
    since = ((today or date.today()) - timedelta(days=30)).isoformat()
    open_ = [j for j in jobs if j["status"] == "in progress"]
    covered = [j["must_have"] for j in open_ if j["must_have"] is not None]
    return {
        "in_progress": len(open_),
        "need_claude": sum(j["warnings"] > 0 for j in open_),
        "sent_30_days": sum(bool(j["sent"]) and j["sent"] >= since for j in jobs),
        "avg_must_have": round(sum(covered) / len(covered), 2) if covered else None,
    }


app = FastAPI(title="Job dashboard", docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")


@app.get("/api/jobs")
def api_jobs():
    jobs = all_jobs()
    return {"jobs": jobs, "cards": cards(jobs)}


def pages(path: Path) -> int | None:
    try:
        return len(PdfReader(path).pages)
    except Exception:  # unreadable PDF: show no count rather than fail the page
        return None


def files_of(folder: Path, job: dict) -> dict:
    """Per language, the PDFs that exist: resume, cover letter, combined (path relative to the job folder)."""
    out = {}
    for lang in ("en", "fr"):
        out[lang] = [{"kind": kind, "name": p.name, "path": p.relative_to(folder).as_posix(), "pages": pages(p),
                      "not_ready": p.name.startswith("_")}
                     for kind in ("resume", "cover", "combined") if (p := pdf(folder, job, kind, lang)).exists()]
    return out


def coverage(results: list[dict], ratio: dict) -> dict:
    out = {}
    for priority in ("must_have", "preferred"):
        rows = [r for r in results if r["priority"] == priority]
        out[priority] = {"ratio": ratio.get(priority), "total": len(rows),
                         **{s: sum(r["status"] == s for r in rows) for s in ("met", "partial", "missing", "uncertain")}}
    return out


def detail(slug: str) -> dict:
    folder = paths.JOBS / slug
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(folder, con):
            raise HTTPException(404, "No such job")
        job, head = offers.load(folder, con), summary(folder, con)
        row = con.execute("SELECT created_at, composed_at, published_at, sent_at, resume_url, cover_letter_url "
                          "FROM offers WHERE folder = ?", (f"jobs/{slug}",)).fetchone()
        base = re.sub(r"-v\d+$", "", slug)
        versions = [f.name for f in offers.all_folders(con) if re.sub(r"-v\d+$", "", f.name) == base]
    review = load_json(paths.review_json(folder))
    overrides = {o["id"]: o for o in job.get("overrides", [])}
    requirements = [{
        "id": r["id"], "description": r["description"], "priority": r["priority"], "status": r["status"],
        "evidence": r.get("quote"), "posting_quote": r.get("posting_quote"), "section": r.get("section"),
        "hint": r.get("suggestion") or r.get("rationale"), "override": overrides.get(r["id"]),
        "terms": [{"term": t["term"], "status": t["status"], "keyword": t.get("keyword")} for t in r.get("terms", [])],
    } for r in review.get("results", [])]
    rank = {"missing": 0, "partial": 1, "uncertain": 2}
    gaps = sorted((r for r in requirements if r["status"] in rank),
                  key=lambda r: (r["priority"] != "must_have", rank[r["status"]]))
    timeline = [{"date": row[k], "event": e} for k, e in (
        ("created_at", "created, posting saved"), ("composed_at", "resume composed"),
        ("published_at", "published"), ("sent_at", "sent"))]
    return {
        **head, "url": job.get("url"), "resume_url": row["resume_url"], "cover_letter_url": row["cover_letter_url"],
        "created": row["created_at"], "versions": versions, "posting": job.get("posting_text", ""),
        "build": {"date": review.get("generated"), "pages": len((review.get("pdf_check") or {}).get("pages", [])) or None},
        "coverage": coverage(requirements, review.get("evidence_coverage") or {}),
        "requirements": requirements, "gaps": gaps, "files": files_of(folder, job),
        "french_version": bool(job.get("french_version")), "timeline": timeline,
    }


@app.get("/api/jobs/{slug}")
def api_job(slug: str):
    return detail(slug)


def inventory(con: sqlite3.Connection) -> dict:
    """skills_inventory.load(), read only (the original opens the db through db.connect)."""
    skills = []
    for sid, name, start, end in con.execute("SELECT id, name_en, start_at, end_at FROM skills ORDER BY lower(name_en)"):
        match = [k for (k,) in con.execute("SELECT keyword FROM skill_keywords WHERE skill_id = ? AND lang = 'en'", (sid,))]
        skills.append({"id": sid, "name": name, "match": match, "start": start, "end": end})
    return {"skills": skills}


@app.get("/api/jobs/{slug}/interview")
def api_interview(slug: str):
    folder = paths.JOBS / slug
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(folder, con):
            raise HTTPException(404, "No such job")
        job, inv = offers.load(folder, con), inventory(con)
    prep = load_json(paths.interview(folder))
    sections = {r["id"]: r.get("section") for r in load_json(paths.review_json(folder)).get("results", [])}
    content = load_json(paths.content(folder))
    skills = [{"name": s["name"], "years": skills_inventory.label(s["years"])}
              for s in skills_inventory.job_skills(job, content, inv) if s["in_job"]]
    return {
        "exists": bool(prep), "generated": prep.get("generated"), "how_to_prepare": prep.get("how_to_prepare", {}),
        "summary": prep.get("summary", {}), "skills": skills,
        # quick fact = a location requirement (no story needed); degrees have no field that marks them
        "topics": [{**t, "quick_fact": sections.get(t["id"]) == "location"} for t in prep.get("topics", [])],
    }


HARD = ("technical", "design", "ai")  # hard skills; soft, language and location never get dates or a level
RANK = {"met": 3, "partial": 2, "uncertain": 1, "missing": 0}


def requirement_terms() -> dict:
    """Every posting term across jobs (case-insensitive), typed through requirement_terms.skill_id -> skills.type,
    with per job its best status and wording from review.json (exact, or synonym when only a keyword matched)."""
    with ro() as con:
        rows = con.execute("SELECT rt.term, rt.skill_id, s.type, s.start_at, s.end_at, o.folder FROM requirement_terms rt "
                           "JOIN requirements r ON r.id = rt.requirement_id JOIN offers o ON o.id = r.offer_id "
                           "LEFT JOIN skills s ON s.id = rt.skill_id").fetchall()
        keywords = {}
        for sid, kw, lang in con.execute("SELECT skill_id, keyword, lang FROM skill_keywords ORDER BY lang, keyword"):
            keywords.setdefault(sid, []).append({"keyword": kw, "lang": lang})
        hard = con.execute(f"SELECT count(*), count(start_at) FROM skills WHERE type IN {HARD}").fetchone()
        jobs = {f.name: summary(f, con) for f in offers.all_folders(con)}

    terms = {}
    for term, sid, typ, start, end, folder in rows:
        t = terms.setdefault(term.casefold(), {"term": term, "skill_id": sid, "type": typ, "start": start, "end": end,
                                               "jobs": {}})
        t["jobs"].setdefault(folder.removeprefix("jobs/"), None)
    for slug in jobs:  # per job: best status of the term and how the resume words it
        for r in load_json(paths.review_json(paths.JOBS / slug)).get("results", []):
            for x in r.get("terms", []):
                t = terms.get(x["term"].casefold())
                if t is None or slug not in t["jobs"]:
                    continue
                seen = t["jobs"][slug] or {"status": "missing", "wording": "absent"}
                if RANK.get(x["status"], 0) >= RANK[seen["status"]]:
                    seen["status"] = x["status"]
                wording = {"exact": "exact", "alias": "synonym"}.get(x.get("keyword"), "absent")
                if seen["wording"] != "exact" and wording != "absent":
                    seen["wording"] = wording
                t["jobs"][slug] = seen

    out = []
    for t in terms.values():
        asked = [{"slug": slug, "company": jobs[slug]["company"], "role": jobs[slug]["role"],
                  "job_status": jobs[slug]["status"], **(seen or {"status": None, "wording": None})}
                 for slug, seen in t["jobs"].items()]
        counts = {s: sum(a["status"] == s for a in asked) for s in ("met", "partial", "missing")}
        is_hard = t["type"] in HARD
        out.append({
            "term": t["term"], "type": t["type"], "hard": is_hard, "jobs": len(asked), **counts,
            "synonym": any(a["wording"] == "synonym" for a in asked),
            "experience": skills_inventory.label(skills_inventory.years(t)) if is_hard else None,
            "start": t["start"], "end": t["end"], "keywords": keywords.get(t["skill_id"], []), "asked": asked,
        })
    out.sort(key=lambda t: (-t["jobs"], t["term"].casefold()))
    return {"terms": out, "jobs": len(jobs), "hard_entries": hard[0], "hard_with_start": hard[1]}


@app.get("/api/requirements")
def api_requirements():
    return requirement_terms()


def new_version(slug: str) -> dict:
    """Copy the job into its next -vN folder with src/new_job.py --from (keeps its tailoring, drops the sent date)."""
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(paths.JOBS / slug, con):
            raise HTTPException(404, "No such job")
    if not WRITE_LOCK.acquire(blocking=False):
        raise HTTPException(409, "Another new version is being created; wait for it to finish")
    try:
        result = subprocess.run([str(PYTHON), "src/new_job.py", "--from", f"jobs/{slug}"], cwd=ROOT,
                                capture_output=True, text=True, timeout=900)
    finally:
        WRITE_LOCK.release()
    created = re.search(r"^Created jobs/(\S+) from ", result.stdout, re.M)
    return {"ok": result.returncode == 0 and bool(created), "slug": created[1] if created else None,
            "output": (result.stdout + result.stderr).strip()}


@app.post("/api/jobs/{slug}/new-version")
def api_new_version(slug: str):
    return new_version(slug)


@app.get("/files/{slug}/{name:path}")
def files(slug: str, name: str):
    folder = paths.JOBS / slug
    path = folder / name
    inside = path.resolve().is_relative_to(folder.resolve()) and "/" not in slug and not slug.startswith(".")
    if not inside or not path.is_file() or path.suffix not in (".pdf", ".md"):
        raise HTTPException(404, "No such file")
    return FileResponse(path, media_type="application/pdf" if path.suffix == ".pdf" else "text/plain; charset=utf-8")


@app.get("/skills")
def skills():
    return RedirectResponse("/requirements", status_code=301)


if (DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")


@app.get("/{page:path}")
def spa(page: str):
    """Every other URL ("/", "/job/<slug>", "/requirements") is a page of the Vue app; it routes on the client."""
    if page.startswith("api/"):
        raise HTTPException(404)
    if (DIST / page).is_file() and page:  # favicon and other files from web/public
        return FileResponse(DIST / page)
    if not (DIST / "index.html").exists():
        raise HTTPException(503, "Front not built: run python3 start.py (or pnpm build in dashboard/web)")
    return FileResponse(DIST / "index.html")
