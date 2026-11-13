"""Local job dashboard: a JSON API under /api plus the built Vue app (dashboard/web/dist) on the same port.

Run from the repo root:  python3 start.py   (or .venv/bin/python -m uvicorn dashboard.app:app --port 8765 after a build)
The app itself only reads: data/resume.db is opened with mode=ro and jobs/ is only read.
Writes run src/ scripts, so their rules hold: "New version" runs src/new_job.py --from (the source folder, sent or not,
is never changed), "Mark as sent" runs src/offers.py sent, interview notes run src/offers.py note, and the Requirements term drawer runs
src/skills_inventory.py, and the Resume page runs src/master.py set line / new-line and the scorers' rescore.
Every other write action in the UI is shown disabled ("not wired yet").
"""

import json
import re
import sqlite3
import subprocess
import sys
import threading
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import offers  # noqa: E402  (load/all_folders take a connection: we pass a read-only one)
import paths  # noqa: E402  (only plain path joins: resume_pdf & co. call stem(), which opens a writable db)
import check_style  # noqa: E402  (check(content) is pure: reads a dict, writes nothing)
import skills_inventory  # noqa: E402  (pure helpers only: job_skills/years/label; its load() opens a writable db)
from db import EN, tr  # noqa: E402  (EN: a JSON column's English text in SQL; tr: that text in Python)

DB = ROOT / "data" / "resume.db"
PYTHON = ROOT / ".venv" / "bin" / "python"
WRITE_LOCK = threading.Lock()  # one script at a time: two new versions at once would pick the same -vN
DIST = Path(__file__).parent / "web" / "dist"
MAX_PAGES = 3
BUILD_PARTS = {"resume": "Resume", "cover": "Cover letter", "resume-fr": "French resume", "cover-fr": "French cover letter"}

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
    """Warnings and info from the last build. Text only: what to do about them is the user's call."""
    notes = []
    if not job.get("requirements"):
        notes.append({"severity": "warning", "text": "No requirements yet"})
    elif review.get("unreviewed"):
        notes.append({"severity": "info", "text": f"{review['unreviewed']} requirements not reviewed"})
    # build.json: each built part's warnings, saying WHY a part is not ready. Jobs built before it existed (and sent
    # jobs, never rebuilt) have no file: fall back to the '_' file alone.
    build = load_json(paths.build_json(folder))
    if pdf(folder, job).name.startswith("_") and not (build.get("resume") or {}).get("warnings"):
        notes.append({"severity": "warning", "text": "Resume marked not ready ('_' file)"})
    for part, label in BUILD_PARTS.items():
        built = build.get(part) or {}
        ready = built.get("ready", True)
        for warning in built.get("warnings", []):
            notes.append({"severity": "info" if ready else "warning",
                          "text": f"{label}{'' if ready else ' not ready'}: {warning}"})
    pages = len((review.get("pdf_check") or {}).get("pages", []))
    if pages > MAX_PAGES:
        notes.append({"severity": "warning", "text": f"Resume is {pages} pages (target {MAX_PAGES})"})
    title = review.get("job_title") or {}
    if title and not title.get("match"):
        notes.append({"severity": title.get("severity", "warning"), "text": title["message"]})
    for part in ("pdf_check", "spelling", "style"):
        for f in (review.get(part) or {}).get("findings", []):
            notes.append({"severity": f["severity"], "text": f["message"]})
    if job.get("french_version") and not pdf(folder, job, lang="fr").exists():
        notes.append({"severity": "warning", "text": "Posting is in French: French version needed"})
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
        "overall": cov.get("overall"), "must_have": cov.get("must_have"), "preferred": cov.get("preferred"),
        "warnings": sum(n["severity"] in ("error", "warning") for n in notes),
        "notes": notes,
        "terms": sorted({t for r in job.get("requirements", []) for t in r.get("terms", [])}, key=str.casefold),
    }


def all_jobs() -> list[dict]:
    """One row per offer: its latest version (by created_at), with how many versions it has. A composition without
    an offer is its own row. Newest first."""
    with ro() as con:
        rows = con.execute("SELECT folder, offer_id, count(*) OVER (PARTITION BY coalesce(offer_id, -id)) AS n, "
                           "row_number() OVER (PARTITION BY coalesce(offer_id, -id) ORDER BY created_at DESC, id DESC) AS k "
                           "FROM compositions ORDER BY created_at DESC, id DESC").fetchall()
        return [{**summary(paths.ROOT / folder, con), "versions": n} for folder, _, n, k in rows if k == 1]


def cards(jobs: list[dict], today: date | None = None) -> dict:
    """The four summary cards of the jobs list, from real data only (None = nothing to average)."""
    since = ((today or date.today()) - timedelta(days=30)).isoformat()
    open_ = [j for j in jobs if j["status"] == "in progress"]
    covered = [j["must_have"] for j in open_ if j["must_have"] is not None]
    return {
        "in_progress": len(open_),
        "with_warnings": sum(j["warnings"] > 0 for j in open_),
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


def sentences(posting: str) -> list[str]:
    """The posting cut into lines and sentences, bullets stripped."""
    parts = (x.strip(" \t-*•·–—") for line in posting.splitlines() for x in re.split(r"(?<=[.!?;])\s+", line))
    return [x for x in parts if x]


def posting_quote(parts: list[str], terms: list[str]) -> str:
    """The first posting sentence using one of the terms: as written (whole words, case ignored, singular or plural),
    else with all its words in any order ("bachelor's degree" in "Bachelor's or Master's degree"). The db keeps only the
    keyword, not where the posting asked for it, so the quote is found again here; '' when no sentence uses it."""
    word = lambda w: rf"(?<!\w){re.escape(re.sub(r'(?<=\w\w)s$', '', w))}s?(?!\w)"
    terms = [t.strip().replace("’", "'") for t in terms if t and t.strip()]
    for test in ([re.compile(word(t), re.I) for t in terms],  # pass 1: the term as written, for every term
                 [re.compile("".join(f"(?=.*{word(w)})" for w in t.split()), re.I) for t in terms]):  # pass 2: its words
        for pattern in test:
            if hit := next((x for x in parts if pattern.search(x.replace("’", "'"))), None):
                return hit
    return ""


FIELD = re.compile(r"experience\[(\d+)\]\.(description|bullets\[(\d+)\])(?: \((.*)\))?")


def line_at(content: dict, field: str) -> dict | None:
    """A check_style field ("summary", "experience[1].bullets[3] (Company)") -> where it is, in words, and its text."""
    if field == "summary":
        return {"where": "Summary", "text": content.get("summary", "")}
    if not (m := FIELD.fullmatch(field)):
        return None
    job = content.get("experience", [])[int(m[1])]
    where = f"{m[4] or job.get('company', '').strip(' ,')} · " + (f"bullet {int(m[3]) + 1}" if m[3] else "description")
    return {"where": where, "text": job["bullets"][int(m[3])] if m[3] else job.get("description", "")}


def repetitions(content: dict) -> list[dict]:
    """Words to vary, from src/check_style.py run on the job's content.json now (saved reports may predate it):
    a word used in many experience lines (overused_word, info), or twice in one line (repeated_word, warning).
    Most repeated first."""
    rows = []
    for f in check_style.check(content)["findings"] if content else []:
        if f["code"] == "overused_word":
            rows += [{"word": w["word"], "count": w["count"], "kind": "across lines",
                      "lines": [x for line in w["lines"] if (x := line_at(content, line["field"]))]}
                     for w in f.get("words", [])]
        elif f["code"] == "repeated_word" and (line := line_at(content, f["field"])):
            for word in re.findall(r"'([^']+)'", f["message"].split(": ", 1)[1]):
                n = len(re.findall(rf"(?<!\w){re.escape(word)}(?!\w)", line["text"], re.I))
                rows.append({"word": word, "count": n, "kind": "in one line", "lines": [line]})
    return sorted(rows, key=lambda r: (-r["count"], r["kind"], r["word"]))


def ignored_keywords(con: sqlite3.Connection) -> set[str]:
    """Keywords of skills set aside (skills.ignored): they count in no job, even where a saved review still lists them."""
    return {k for (k,) in con.execute("SELECT k.keyword FROM skill_keywords k JOIN skills s ON s.id = k.skill_id "
                                      "WHERE s.ignored = 1")}


def set_aside(result: dict, ignored: set[str]) -> bool:
    """A saved review result whose every term is a set-aside skill (sent jobs keep reviews made before it was set aside)."""
    terms = [t["term"].lower() for t in result.get("terms", [])]
    return bool(terms) and all(t in ignored for t in terms)


def coverage(results: list[dict], ratio: dict) -> dict:
    out = {}
    for priority in ("overall", "must_have", "preferred"):  # overall: every requirement (review.json v3; None before)
        rows = [r for r in results if priority in ("overall", r["priority"]) and r["status"] != "set aside"]
        out[priority] = {"ratio": ratio.get(priority), "total": len(rows),
                         **{s: sum(r["status"] == s for r in rows) for s in ("met", "partial", "missing", "uncertain")}}
    return out


def detail(slug: str) -> dict:
    folder = paths.JOBS / slug
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(folder, con):
            raise HTTPException(404, "No such job")
        job, head = offers.load(folder, con), summary(folder, con)
        comp = offers.composition(folder, con)
        offer = con.execute("SELECT created_at, resume_url FROM offers WHERE id = ?", (comp["offer_id"],)).fetchone() \
            if comp["offer_id"] else None
        # versions = the compositions of the same offer, oldest first (no version number in the db: created_at orders them)
        types = dict(con.execute("SELECT k.keyword, s.type FROM skill_keywords k JOIN skills s ON s.id = k.skill_id"))
        ignored = ignored_keywords(con)
        versions = [f.removeprefix("jobs/") for (f,) in con.execute(
            "SELECT folder FROM compositions WHERE offer_id = ? ORDER BY created_at, id", (comp["offer_id"],))] \
            if offer else [slug]
    review = load_json(paths.review_json(folder))
    parts = sentences(job.get("posting_text", ""))
    overrides = {o["id"]: o for o in job.get("overrides", [])}
    requirements = [{
        "id": r["id"], "description": r["description"], "priority": r["priority"],
        "status": "set aside" if set_aside(r, ignored) else r["status"],
        # the skill type of its first typed term (None = not typed yet)
        "type": r.get("type") or next((types[k] for t in r.get("terms", []) if types.get(k := t["term"].lower())), None),
        "evidence": r.get("quote"), "posting_quote": r.get("posting_quote") or posting_quote(parts, [t["term"] for t in r.get("terms", [])]), "section": r.get("section"),
        "hint": r.get("suggestion") or r.get("rationale"), "override": overrides.get(r["id"]),
        "terms": [{"term": t["term"], "status": t["status"], "keyword": t.get("keyword")} for t in r.get("terms", [])],
    } for r in review.get("results", [])]
    timeline = [{"date": offer and offer["created_at"], "event": "posting saved"},
                {"date": comp["created_at"], "event": "version created"},
                {"date": comp["sent_at"], "event": "sent"}]
    return {
        **head, "url": job.get("url"), "resume_url": offer and offer["resume_url"],
        "created": comp["created_at"][:10], "versions": versions, "posting": job.get("posting_text", ""),
        "build": {"date": review.get("generated"), "pages": len((review.get("pdf_check") or {}).get("pages", [])) or None},
        "coverage": coverage(requirements, review.get("evidence_coverage") or {}),
        "requirements": requirements, "files": files_of(folder, job),
        "french_version": bool(job.get("french_version")), "timeline": timeline,
        "repetitions": repetitions(load_json(paths.content(folder))),
    }


@app.get("/api/jobs/{slug}")
def api_job(slug: str):
    return detail(slug)


@app.post("/api/jobs/{slug}/refresh")
def api_refresh(slug: str):
    """Run the search again and save it (src/review_ats.py). Sent jobs too: it rewrites only their review/ reports
    (which keywords the sent PDFs contain), never the PDFs, content or requirements (AGENTS.md exception)."""
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(paths.JOBS / slug, con):
            raise HTTPException(404, "No such job")
    return script_result(run_script("src/review_ats.py", "--job", f"jobs/{slug}", "--no-network"))


def inventory(con: sqlite3.Connection) -> dict:
    """skills_inventory.load(), read only (the original opens the db through db.connect)."""
    skills = []
    for sid, name, kind, start, end in con.execute(f"SELECT id, {EN.format('name')}, type, start_at, end_at FROM skills "
                                                   f"ORDER BY {EN.format('name')}"):
        match = [k for (k,) in con.execute("SELECT keyword FROM skill_keywords WHERE skill_id = ? AND lang = 'en' "
                                           "AND keyword <> ?", (sid, name))]
        skills.append({"id": sid, "name": name, "type": kind, "match": match, "start": start, "end": end})
    return {"skills": skills}


def keyword_of(topic: dict) -> str:
    """The requirement keyword behind an interview topic: "java (10+ years)" -> "java"."""
    return re.sub(r"\s*\(.*\)$", "", topic.get("requirement", "")).strip().lower()


class Note(BaseModel):
    keyword: str = Field(max_length=100, pattern=r"^[^\n\r]+$")  # one line
    note: str = Field(default="", max_length=5000)  # empty: delete


@app.post("/api/jobs/{slug}/notes")
def api_note(slug: str, body: Note):
    """Save one interview note with src/offers.py note. Notes are on the offer's requirement in the db, never in the
    job folder, so they work on sent jobs and every version of the offer shares them."""
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(paths.JOBS / slug, con):
            raise HTTPException(404, "No such job")
        asked = con.execute("SELECT 1 FROM requirements r JOIN skill_keywords k ON k.id = r.keyword_id JOIN compositions c "
                            "ON c.offer_id = r.offer_id WHERE c.folder = ? AND k.keyword = ?",
                            (f"jobs/{slug}", body.keyword.strip().lower())).fetchone()
    if not asked:
        raise HTTPException(404, f"'{body.keyword}' is not a requirement of this job")
    return script_result(run_script("src/offers.py", "note", f"jobs/{slug}", body.keyword.strip().lower(),
                                    *([body.note.strip()] if body.note.strip() else [])))


@app.get("/api/jobs/{slug}/interview")
def api_interview(slug: str):
    folder = paths.JOBS / slug
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(folder, con):
            raise HTTPException(404, "No such job")
        job, inv = offers.load(folder, con), inventory(con)
        ignored = ignored_keywords(con)
        notes = {kw: {"note": n, "updated": u} for kw, n, u in con.execute(
            "SELECT k.keyword, n.note, n.updated_at FROM interview_notes n JOIN requirements r ON r.id = n.requirement_id "
            "JOIN skill_keywords k ON k.id = r.keyword_id WHERE r.offer_id = ?", (job.get("offer_id"),))}
    prep = load_json(paths.interview(folder))
    topics = [t for t in prep.get("topics", []) if keyword_of(t) not in ignored]  # set-aside skills: nothing to prepare
    content = load_json(paths.content(folder))
    skills = [{"name": s["name"], "years": skills_inventory.label(s["years"])}
              for s in skills_inventory.job_skills(job, content, inv) if s["in_job"]]
    return {
        "exists": bool(prep), "generated": prep.get("generated"), "how_to_prepare": prep.get("how_to_prepare", {}),
        "summary": dict(Counter(t["focus"] for t in topics)), "skills": skills,
        "topics": [{**t, **notes.get(keyword_of(t), {"note": "", "updated": None}), "keyword": keyword_of(t),
                    "posting_says": t.get("posting_says") or posting_quote(
            sentences(job.get("posting_text", "")), [re.sub(r"\s*\(.*\)$", "", t.get("requirement", "")), *t.get("terms_not_met", [])])}
            for t in topics],
    }


HARD = ("programming_language", "technology", "technical", "design", "ai")  # hard skills; soft, language, location and education never get dates or a level
SKILL_TYPES = HARD + ("soft", "language", "location", "education")  # same as src/db.py SKILL_TYPES
RANK = {"met": 3, "partial": 2, "uncertain": 1, "missing": 0}


def requirement_terms() -> dict:
    """Every requirement keyword across jobs, typed by its skill, with per job (composition of the offer asking for it)
    its best status and wording from review.json (exact, or synonym when only a keyword matched).
    A requirement points to a keyword, which belongs to one skill: a type or keyword added later shows everywhere."""
    with ro() as con:
        rows = con.execute("SELECT k.keyword, k.skill_id, c.folder FROM requirements r "
                           "JOIN skill_keywords k ON k.id = r.keyword_id "
                           "JOIN compositions c ON c.offer_id = r.offer_id").fetchall()
        skills = {sid: {"id": sid, "name": name, "type": typ, "start": start, "end": end, "ignored": bool(ignored),
                        "keywords": []}
                  for sid, name, typ, start, end, ignored in con.execute(
                      f"SELECT id, {EN.format('name')}, type, start_at, end_at, ignored FROM skills")}
        for sid, kw, lang in con.execute("SELECT skill_id, keyword, lang FROM skill_keywords ORDER BY lang, keyword"):
            skills[sid]["keywords"].append({"keyword": kw, "lang": lang})
        hard = con.execute(f"SELECT count(*), count(start_at) FROM skills WHERE type IN {HARD}").fetchone()
        jobs = {f.name: summary(f, con) for f in offers.all_folders(con)}
    terms = {}
    for term, sid, folder in rows:
        skill = skills.get(sid, {})
        t = terms.setdefault(term.casefold(), {"term": term.lower(),  # one spelling, lowercase like the skills
                                               "skill": skill.get("name"), "type": skill.get("type"),
                                               "start": skill.get("start"), "end": skill.get("end"),
                                               "ignored": skill.get("ignored", False),
                                               "keywords": skill.get("keywords", []), "jobs": {}})
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
        if t["ignored"]:  # set aside: counts nowhere, whatever the saved reviews say
            asked = [{**a, "status": "set aside"} for a in asked]
        counts = {s: sum(a["status"] == s for a in asked) for s in ("met", "partial", "missing")}
        is_hard = t["type"] in HARD
        out.append({
            "term": t["term"], "type": t["type"], "hard": is_hard, "jobs": len(asked), **counts,
            "synonym": any(a["wording"] == "synonym" for a in asked),
            "experience": skills_inventory.label(skills_inventory.years(t)) if is_hard else None,
            "skill": t["skill"], "ignored": t["ignored"], "start": t["start"], "end": t["end"], "keywords": t["keywords"], "asked": asked,
        })
    out.sort(key=lambda t: (-t["jobs"], t["term"].casefold()))
    return {"terms": out, "jobs": len(jobs), "hard_entries": hard[0], "hard_with_start": hard[1]}


@app.get("/api/requirements")
def api_requirements():
    return requirement_terms()


def run_script(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    """Run one src/ script (the dashboard's only way to write). One at a time: two runs could clash on the same db."""
    if not WRITE_LOCK.acquire(blocking=False):
        raise HTTPException(409, "Another change is still running; wait for it to finish")
    try:
        return subprocess.run([str(PYTHON), *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    finally:
        WRITE_LOCK.release()


def new_version(slug: str) -> dict:
    """Copy the job into its next -vN folder with src/new_job.py --from: summary, title, skills and cover letters are
    copied, the experience lines are composed again from the library (kept as they are when the job has no
    requirements), and the sent date is dropped. The source folder is never changed."""
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(paths.JOBS / slug, con):
            raise HTTPException(404, "No such job")
    result = run_script("src/new_job.py", "--from", f"jobs/{slug}")
    created = re.search(r"^Created jobs/(\S+) from ", result.stdout, re.M)
    return {"ok": result.returncode == 0 and bool(created), "slug": created[1] if created else None,
            "output": (result.stdout + result.stderr).strip()}


class Sent(BaseModel):
    date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")  # default: today


@app.post("/api/jobs/{slug}/sent")
def api_mark_sent(slug: str, body: Sent):
    """Mark the job as sent with src/offers.py sent: it is then frozen (no rebuild, edit or republish)."""
    with ro() as con:
        if "/" in slug or slug.startswith(".") or not offers.exists(paths.JOBS / slug, con):
            raise HTTPException(404, "No such job")
        sent = offers.load(paths.JOBS / slug, con).get("sent")
    if sent:
        raise HTTPException(409, f"Already sent on {sent}")
    if body.date:
        try:
            if date.fromisoformat(body.date) > date.today():
                raise HTTPException(422, "The date is in the future")
        except ValueError:
            raise HTTPException(422, "Not a date") from None
    return script_result(run_script("src/offers.py", "sent", f"jobs/{slug}", *([body.date] if body.date else [])))


@app.post("/api/jobs/{slug}/new-version")
def api_new_version(slug: str):
    return new_version(slug)


# Requirements page, term drawer: type, dates (hard skills) and keywords, through src/skills_inventory.py.
TEXT = r"^[^\n\r]+$"  # one line, not empty
MONTH = r"^\d{4}(-(0[1-9]|1[0-2]))?$"  # YYYY or YYYY-MM, as skills_inventory expects


class TypeChange(BaseModel):
    term: str = Field(max_length=100, pattern=TEXT)
    type: str


class Dates(BaseModel):
    skill: str = Field(max_length=100, pattern=TEXT)
    start: str = Field(pattern=MONTH)
    end: str | None = Field(default=None, pattern=MONTH)


class Keyword(BaseModel):
    skill: str = Field(max_length=100, pattern=TEXT)
    keyword: str = Field(max_length=80, pattern=TEXT)
    lang: str = Field(default="en", pattern="^(en|fr)$")


def skill_named(name: str) -> sqlite3.Row | None:
    with ro() as con:
        return con.execute(f"SELECT id, {EN.format('name')} AS name_en, type FROM skills "
                           f"WHERE lower({EN.format('name')}) = lower(?)", (name,)).fetchone()


def script_result(result: subprocess.CompletedProcess) -> dict:
    return {"ok": result.returncode == 0, "output": (result.stdout + result.stderr).strip()}


@app.post("/api/skills/type")
def api_skill_type(body: TypeChange):
    """Give a term (or its skill) a type; a term with no entry gets one, with that type and no dates."""
    if body.type not in SKILL_TYPES:
        raise HTTPException(422, f"Unknown type; use one of: {', '.join(SKILL_TYPES)}")
    out = script_result(run_script("src/skills_inventory.py", "type", body.term.strip(), body.type))
    if out["ok"]:  # the type weighs in the coverage: recompute the reviews it changes
        out["reviewed"] = rereview(body.term.strip())
    return out


def rereview(term: str) -> list[str]:
    """Run src/review_ats.py again for the jobs whose requirements use that term's skill, sent ones included (only their
    review/ reports are rewritten, never what was sent)."""
    with ro() as con:
        folders = [f for (f,) in con.execute(
            "SELECT DISTINCT c.folder FROM requirements r JOIN skill_keywords k ON k.id = r.keyword_id "
            "JOIN compositions c ON c.offer_id = r.offer_id WHERE k.skill_id IN "
            f"(SELECT skill_id FROM skill_keywords WHERE keyword = lower(?) UNION "
            f"SELECT id FROM skills WHERE lower({EN.format('name')}) = lower(?)) ORDER BY c.folder", (term, term))]
    return [f.removeprefix("jobs/") for f in folders
            if run_script("src/review_ats.py", "--job", f, "--no-network").returncode == 0]


class Ignore(BaseModel):
    skill: str = Field(max_length=100, pattern=TEXT)
    ignored: bool


@app.post("/api/skills/ignore")
def api_skill_ignore(body: Ignore):
    """Set a skill aside (it counts in no job's requirements or scoring) or count it again, with
    src/skills_inventory.py ignore; then recompute the reviews of the open jobs asking for it (sent ones keep theirs)."""
    skill = skill_named(body.skill)
    if skill is None:
        raise HTTPException(404, "No such skill: give the term a type first")
    out = script_result(run_script("src/skills_inventory.py", "ignore", skill["name_en"], *([] if body.ignored else ["off"])))
    if out["ok"]:
        out["reviewed"] = rereview(skill["name_en"])
    return out


@app.post("/api/skills/dates")
def api_skill_dates(body: Dates):
    skill = skill_named(body.skill)
    if skill is None:
        raise HTTPException(404, "No such skill: give the term a type first")
    if skill["type"] not in HARD:
        raise HTTPException(422, "Only hard skills (technical, design, AI) have dates")
    if body.end and skills_inventory.months(body.end, end_of_period=True) < skills_inventory.months(body.start):
        raise HTTPException(422, "The end date is before the start date")
    return script_result(run_script("src/skills_inventory.py", "set", skill["name_en"], body.start,
                                    *([body.end] if body.end else [])))


@app.post("/api/skills/keyword")
def api_skill_keyword(body: Keyword):
    skill = skill_named(body.skill)
    if skill is None:  # the keyword command would create the skill typed 'technical'; ask for the type first
        raise HTTPException(404, "No such skill: give the term a type first")
    keyword = body.keyword.strip()
    with ro() as con:
        taken = con.execute(f"SELECT {EN.format('s.name')} FROM skill_keywords k JOIN skills s ON s.id = k.skill_id "
                            f"WHERE k.keyword = lower(?) AND k.lang = ?", (keyword, body.lang)).fetchone()
    if taken:
        raise HTTPException(409, f"'{keyword}' already counts as {taken[0]}")
    return script_result(run_script("src/skills_inventory.py", "keyword", skill["name_en"], keyword, body.lang))


@app.get("/api/skills")
def api_skills():
    """Every skill with its type and keywords: the drawer's "move into another skill" search."""
    with ro() as con:
        skills = {sid: {"name": name, "type": typ, "keywords": []} for sid, name, typ in con.execute(
            f"SELECT id, {EN.format('name')}, type FROM skills ORDER BY {EN.format('name')}")}
        for sid, kw, lang in con.execute("SELECT skill_id, keyword, lang FROM skill_keywords ORDER BY lang, keyword"):
            skills[sid]["keywords"].append({"keyword": kw, "lang": lang})
    return {"skills": list(skills.values())}


class Move(BaseModel):
    keyword: str = Field(max_length=80, pattern=TEXT)
    skill: str = Field(max_length=100, pattern=TEXT)


@app.post("/api/skills/move")
def api_skill_move(body: Move):
    """Merge: the keyword now counts as that skill; its old skill is dropped once it has no keyword left. The reviews
    of the open jobs asking for it are recomputed (the type, and so the weighted coverage, may change)."""
    keyword = body.keyword.strip().lower()
    target = skill_named(body.skill)
    if target is None:
        raise HTTPException(404, "No such skill")
    with ro() as con:
        owners = {sid for (sid,) in con.execute("SELECT skill_id FROM skill_keywords WHERE keyword = ?", (keyword,))}
    if not owners:
        raise HTTPException(404, f"No keyword '{keyword}'")
    if owners == {target["id"]}:
        raise HTTPException(409, f"'{keyword}' already counts as {target['name_en']}")
    out = script_result(run_script("src/skills_inventory.py", "move", keyword, target["name_en"]))
    if out["ok"]:
        out["reviewed"] = rereview(keyword)
    return out


# ---------- /resume: the master resume, bloc by bloc, with its candidates and reviews ----------
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def ym(value: str, end: bool = False) -> tuple[int, int]:
    """'2021-08' -> (2021, 8); a year alone covers the whole year."""
    y, _, m = value.partition("-")
    return int(y), int(m) if m else (12 if end else 1)


def month_label(value: str | None) -> str | None:
    if not value:
        return None
    y, _, m = value.partition("-")
    return f"{MON[int(m) - 1]} {y}" if m else y


def months(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Inclusive count of months from a to b."""
    return (b[0] - a[0]) * 12 + b[1] - a[1] + 1


def keyword_finder(con):
    """Skill keywords found in a text, as on the board: whole words (same matching as src/db_sync.py), set-aside
    skills left out; each with 'asked' (a job requirement uses the skill, with how many offers) or 'known'."""
    import db_sync  # noqa: E402  (word_in and skill_words only read)
    asked = dict(con.execute("SELECT k.skill_id, count(DISTINCT r.offer_id) FROM requirements r "
                             "JOIN skill_keywords k ON k.id = r.keyword_id GROUP BY k.skill_id").fetchall())
    ignored = {i for (i,) in con.execute("SELECT id FROM skills WHERE ignored")}
    words = [(sid, names) for sid, names in db_sync.skill_words(con) if sid not in ignored]

    def find(text: str) -> list[dict]:
        out = []
        for sid, names in words:
            hit = next((n for n in names if len(n) > 1 and db_sync.word_in(n, text)), None)
            if hit:
                out.append({"name": hit, "status": "asked" if sid in asked else "known", "jobs": asked.get(sid, 0)})
        return sorted(out, key=lambda k: (-k["jobs"], k["name"]))
    return find


def chip(name: str, find) -> dict:
    """A token listed on the resume (a project's tech): its skill status, or 'new' when no skill has that keyword."""
    hits = [k for k in find(name) if k["name"].casefold() == name.casefold()]
    return hits[0] | {"name": name} if hits else {"name": name, "status": "new", "jobs": 0}


def resume_data(comp_id: int | None = None) -> dict:
    """Everything a resume page shows, read only. comp_id: one composition, whose recorded choices (offer_lines,
    composition_profile) are the candidates in use, its lines in its own order. None: the best candidate of each bloc
    (src/pick.py: best review, English and French text). Each slider lists the bloc's approved candidates, newest first."""
    import pick  # noqa: E402  (best() and candidates() only read)
    with ro() as con:
        find = keyword_finder(con)
        comp_lines, comp_profile, comp = {}, {}, None
        if comp_id is not None:
            comp = con.execute("SELECT * FROM compositions WHERE id = ?", (comp_id,)).fetchone()
            if comp is None:
                raise HTTPException(404, "No such resume")
            for aid, did, pos in con.execute("SELECT d.activity_id, d.id, l.position FROM offer_lines l JOIN bloc_descriptions d "
                                             "ON d.id = l.description_id WHERE l.composition_id = ? ORDER BY l.position", (comp_id,)):
                comp_lines[pos] = (aid, did)  # one row per recorded line: two lines may share an activity
            comp_profile = dict(con.execute("SELECT p.key, p.id FROM composition_profile c JOIN bloc_profile p "
                                            "ON p.id = c.profile_id WHERE c.composition_id = ?", (comp_id,)).fetchall())
        tr_ = lambda v, lang="en": (json.loads(v).get(lang) or "") if v else ""
        def versions(key, quality):  # a profile bloc's versions, newest first, the one the master uses marked
            cands = pick.profile_candidates(con, key)
            chosen, _, warn = pick.best(cands, ("en", "fr"), quality=quality)
            if comp is not None:  # this resume's own version
                chosen, warn = next((c for c in cands if c["id"] == comp_profile.get(key)), None), None
            if key == "role" and warn:  # the role has no rubric: "no reviewed candidate" is expected, not a warning
                warn = warn.replace("; no reviewed candidate; the newest is used", "").replace(
                    "no reviewed candidate; the newest is used", "") or None
            cands.sort(key=lambda c: (c["created_at"] or "", c["id"]), reverse=True)
            return {"warning": warn, "candidates": [
                {"id": c["id"], "text": c["text_en"], "fr": tr_(c["text"], "fr"), "created_at": c["created_at"],
                 "used": bool(chosen) and c["id"] == chosen["id"], "review": json.loads(c["score"]) if c["score"] else None}
                for c in cands]}
        role, summary = versions("role", pick.line_quality), versions("summary", pick.summary_quality)
        used = lambda v: next((c for c in v["candidates"] if c["used"]), None)
        profile = {"role": role, "summary": summary, "review": (used(summary) or {}).get("review")}
        role_text, summary_text = (used(role) or {}).get("text", ""), (used(summary) or {}).get("text", "")
        profile["keywords"] = find(f"{role_text} {summary_text}")
        exps = con.execute(f"SELECT e.id, {EN.format('c.name')} AS company, {EN.format('e.role')} AS role, k.start_at, "
                           "k.end_at FROM bloc_experiences e JOIN contracts k ON k.id = e.contract_id "
                           "JOIN companies c ON c.id = k.company_id ORDER BY k.start_at DESC, e.id").fetchall()
        experiences = []
        for e in exps:
            lines = []
            acts = [(aid, label, None) for aid, label in con.execute(
                "SELECT id, label FROM bloc_activities WHERE experience_id = ? AND active = 1 ORDER BY sort_order", (e["id"],))]
            if comp is not None:  # the lines this resume uses, in its order (inactive activities included)
                labels = dict(con.execute("SELECT id, label FROM bloc_activities WHERE experience_id = ?", (e["id"],)).fetchall())
                acts = [(aid, labels[aid], pos) for pos, (aid, _) in sorted(comp_lines.items()) if aid in labels]
            for aid, label, pos in acts:
                cands = pick.candidates(con, aid)
                chosen, _, warn = pick.best(cands, ("en", "fr"))
                if comp is not None:
                    chosen, warn = next((c for c in cands if c["id"] == comp_lines[pos][1]), None), None
                if not chosen:
                    continue
                cands.sort(key=lambda c: (c["created_at"] or "", c["id"]), reverse=True)
                lines.append({"activity_id": aid, "position": pos, "key": f"{aid}-{pos}", "label": label,
                              "kind": chosen["kind"], "warning": warn,
                              "chosen_id": chosen["id"], "keywords": find(chosen["text_en"]),
                              "candidates": [{"id": c["id"], "text": c["text_en"], "fr": tr_(c["text"], "fr"),
                                              "created_at": c["created_at"], "used": c["id"] == chosen["id"],
                                              "review": json.loads(c["score"]) if c["score"] else None} for c in cands]})
            seen = {}
            for line in lines:
                for k in line["keywords"]:
                    seen.setdefault(k["name"], k)
            start, end = ym(e["start_at"]), ym(e["end_at"], end=True) if e["end_at"] else None
            experiences.append({"id": e["id"], "company": e["company"], "role": e["role"],
                                "from": month_label(e["start_at"]), "to": month_label(e["end_at"]),
                                "months": months(start, end) if end else None,
                                "keywords": sorted(seen.values(), key=lambda k: (-k["jobs"], k["name"])), "lines": lines})
        for newer, older in zip(exps, exps[1:]):  # a month with no experience between two jobs is a gap
            last = ym(older["end_at"], end=True) if older["end_at"] else None
            first = ym(newer["start_at"])
            n = months(last, first) - 2 if last else 0
            if n > 0:
                g_from = (last[0] + last[1] // 12, last[1] % 12 + 1)
                g_to = (first[0] - (first[1] == 1), (first[1] - 2) % 12 + 1)
                gap = {"from": f"{MON[g_from[1] - 1]} {g_from[0]}", "to": f"{MON[g_to[1] - 1]} {g_to[0]}", "months": n,
                       "after": older["company"], "before": newer["company"],
                       "ended": month_label(older["end_at"]), "started": month_label(newer["start_at"])}
                next(x for x in experiences if x["id"] == older["id"])["gap_after"] = gap
        blocs = {
            "projects": [{"title": r["name"], "keywords": [chip(t.strip(), find) for t in tr_(r["tech"]).split("·")
                                                            if t.strip()]} for r in con.execute("SELECT * FROM bloc_projects ORDER BY id")],
            "education": [{"title": f"{tr_(r['degree'])} · {tr_(r['institution'])}",
                           "keywords": find(f"{tr_(r['degree'])} {tr_(r['institution'])}")}
                          for r in con.execute("SELECT * FROM bloc_education ORDER BY id")],
            "languages": [{"title": f"{tr_(r['name'])} · {tr_(r['level'])}", "keywords": find(tr_(r["name"]))}
                          for r in con.execute("SELECT * FROM bloc_languages ORDER BY sort_order")],
            "certifications": [{"title": f"{r['name']} · {r['issuer']}", "keywords": find(f"{r['name']} {r['issuer']}")}
                               for r in con.execute("SELECT * FROM bloc_certifications ORDER BY id")],
        }
    used = [c["review"] for x in experiences for line in x["lines"] for c in line["candidates"] if c["used"]]
    scored = [r for r in used if r]
    crit = ("result", "evidence", "contribution", "clarity")
    rev = profile["review"]
    bloc_kw = {k["name"].casefold(): k["status"] for items in blocs.values() for i in items for k in i["keywords"]}
    score = {
        "lines": len(used), "scored": len(scored), "unscored": len(used) - len(scored),
        "ready": sum(r["verdict"] == "Ready" for r in scored),
        "total": sum(r["total"] for r in scored), "max": 8 * len(scored),
        "average": round(sum(r["total"] for r in scored) / len(scored), 1) if scored else None,
        "criteria": {c: round(sum(r["scores"][c] for r in scored) / len(scored), 1) if scored else None for c in crit},
        "match": {m: sum(r["claim_evidence_match"] == m for r in scored) for m in ("supports", "partial", "missing", "mismatch")},
        "low": sum(r["total"] < 5 for r in scored),
        "summary": {k: rev[k]["score"] for k in ("name", "fame", "aim")} | {"verdict": rev["verdict"]} if rev else None,
        "keywords": {"total": len(bloc_kw), **{s: sum(v == s for v in bloc_kw.values()) for s in ("asked", "known", "new")}},
    }
    # Ready only when every line and the summary pass (the rubrics' resume-wide rule)
    score["verdict"] = "Ready" if used and score["ready"] == len(used) and rev and rev["verdict"] == "ready" else "Revise"
    limits = {"bullet": check_style.MAX_BULLET_WORDS, "summary": check_style.MAX_SUMMARY_WORDS}  # the style check's word limits
    out = {"score": score, "profile": profile, "experiences": experiences, "blocs": blocs, "limits": limits}
    if comp is not None:
        out["resume"] = next(r for r in resumes_list() if r["id"] == comp["id"])
    return out


def resumes_list() -> list[dict]:
    """Every composition, with or without an offer, newest first, scored from the line candidates it uses (sum of
    totals ÷ 8 per line, as the Resume score) and the review of the summary version it uses."""
    with ro() as con:
        out = []
        for c in con.execute(f"SELECT c.*, o.title, {EN.format('co.name')} AS company FROM compositions c LEFT JOIN offers o "
                             "ON o.id = c.offer_id LEFT JOIN companies co ON co.id = o.company_id "
                             "ORDER BY c.created_at DESC, c.id DESC").fetchall():
            reviews = [json.loads(sc) if sc else None for (sc,) in con.execute(
                "SELECT d.score FROM offer_lines l JOIN bloc_descriptions d ON d.id = l.description_id "
                "WHERE l.composition_id = ?", (c["id"],))]
            scored = [r for r in reviews if r]
            summ = con.execute("SELECT p.score FROM composition_profile cp JOIN bloc_profile p ON p.id = cp.profile_id "
                               "WHERE cp.composition_id = ? AND p.key = 'summary'", (c["id"],)).fetchone()
            out.append({"id": c["id"], "slug": c["folder"].removeprefix("jobs/"), "name": c["name"] or c["folder"].removeprefix("jobs/"),
                        "offer": f"{c['company']} · {c['title']}" if c["title"] else None, "offer_id": c["offer_id"],
                        "created": (c["created_at"] or "")[:10], "sent": c["sent_at"], "approved": c["approved_at"],
                        "score": round(100 * sum(r["total"] for r in scored) / (8 * len(scored))) if scored else None,
                        "lines": len(reviews), "scored": len(scored), "ready": sum(r["verdict"] == "Ready" for r in scored),
                        "summary": json.loads(summ[0])["verdict"] if summ and summ[0] else None})
        return out


@app.get("/api/resume")
def api_resume():
    return resume_data()


@app.get("/api/resumes")
def api_resumes():
    with ro() as con:
        offers_ = [{"id": i, "label": f"{tr(n)} · {t}"} for i, n, t in con.execute(
            "SELECT o.id, c.name, o.title FROM offers o JOIN companies c ON c.id = o.company_id ORDER BY o.created_at DESC")]
    return {"resumes": resumes_list(), "offers": offers_}


@app.get("/api/resumes/{comp_id}")
def api_resume_one(comp_id: int):
    return resume_data(comp_id)


def folder_of(comp_id: int) -> str:
    with ro() as con:
        row = con.execute("SELECT folder FROM compositions WHERE id = ?", (comp_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "No such resume")
    return row[0]


class NewResume(BaseModel):
    name: str = Field(max_length=120, pattern=TEXT)
    offer_id: int | None = None
    from_id: int | None = None  # copy another resume's choices


@app.post("/api/resumes")
def api_resume_new(body: NewResume):
    """A new resume (src/resumes.py new): the best candidate of each bloc, or a copy of another resume's choices."""
    args = ["src/resumes.py", "new", body.name.strip()]
    if body.offer_id is not None:
        args += ["--offer", str(body.offer_id)]
    if body.from_id is not None:
        args += ["--from", folder_of(body.from_id)]
    out = script_result(run_script(*args))
    if out["ok"]:
        with ro() as con:
            out["id"] = con.execute("SELECT max(id) FROM compositions").fetchone()[0]
    return out


class Switch(BaseModel):
    bloc: str = Field(pattern=r"^(\d+|role|summary)$")  # an activity id, or role / summary
    candidate: int
    position: int | None = None  # the line's position in the resume (two lines may share an activity)


@app.post("/api/resumes/{comp_id}/switch")
def api_resume_switch(comp_id: int, body: Switch):
    """This resume uses another candidate for one bloc (src/resumes.py switch; refused on a sent resume)."""
    return script_result(run_script("src/resumes.py", "switch", folder_of(comp_id), body.bloc, str(body.candidate),
                                    *([] if body.position is None else [str(body.position)])))


class Edit(BaseModel):
    bloc: str = Field(pattern=r"^(\d+|role|summary)$")
    en: str = Field(max_length=1200, pattern=TEXT)
    fr: str = Field(max_length=1200, pattern=TEXT)
    position: int | None = None


@app.post("/api/resumes/{comp_id}/edit")
def api_resume_edit(comp_id: int, body: Edit):
    """A new version of one bloc, saved as a candidate and used in this resume (src/resumes.py edit)."""
    return script_result(run_script("src/resumes.py", "edit", folder_of(comp_id), body.bloc, body.en.strip(), body.fr.strip(),
                                    *([] if body.position is None else [str(body.position)]), timeout=600))


class Preview(BaseModel):
    bloc: str | None = Field(default=None, pattern=r"^(\d+|role|summary)$")  # none: the resume as it is
    candidate: int | None = None
    position: int | None = None


@app.post("/api/resumes/{comp_id}/preview")
def api_resume_preview(comp_id: int, body: Preview):
    """A temporary PDF of this resume with one candidate swapped in (src/resumes.py preview): nothing is changed."""
    args = ["src/resumes.py", "preview", folder_of(comp_id)]
    if body.bloc is not None and body.candidate is not None:
        args += [body.bloc, str(body.candidate), *([] if body.position is None else [str(body.position)])]
    result = run_script(*args, timeout=300)
    line = next((l for l in result.stdout.splitlines() if l.startswith("PREVIEW ")), None)
    if result.returncode or not line:
        return script_result(result)
    return {"ok": True, **json.loads(line.removeprefix("PREVIEW ")), "url": f"/previews/{json.loads(line[8:])['pdf']}"}


@app.get("/previews/{name}")
def preview_file(name: str):
    path = ROOT / "data" / "cache" / "preview" / name
    if not re.fullmatch(r"[a-z0-9-]+\.pdf", name) or not path.is_file():
        raise HTTPException(404, "No such preview")
    return FileResponse(path, media_type="application/pdf")


class Rename(BaseModel):
    name: str = Field(max_length=120, pattern=TEXT)


@app.post("/api/resumes/{comp_id}/name")
def api_resume_rename(comp_id: int, body: Rename):
    return script_result(run_script("src/resumes.py", "name", folder_of(comp_id), body.name.strip()))


class Approve(BaseModel):
    approved: bool


@app.post("/api/resumes/{comp_id}/approve")
def api_resume_approve(comp_id: int, body: Approve):
    return script_result(run_script("src/resumes.py", "approve", folder_of(comp_id), *([] if body.approved else ["off"])))


class NewCandidate(BaseModel):
    id: int  # the activity (a new candidate of a line) or the experience (its next line)
    en: str = Field(max_length=600, pattern=TEXT)
    fr: str = Field(max_length=600, pattern=TEXT)  # required: the master resume needs both languages


@app.post("/api/resume/line")
def api_resume_line(body: NewCandidate):
    """A new candidate for a line: src/master.py set line (scored, then the best one is used)."""
    return script_result(run_script("src/master.py", "set", "line", str(body.id), body.en, body.fr))


@app.post("/api/resume/new-line")
def api_resume_new_line(body: NewCandidate):
    """An experience's next line, as a new activity: src/master.py set new-line."""
    return script_result(run_script("src/master.py", "set", "new-line", str(body.id), body.en, body.fr))


class ProfileVersion(BaseModel):
    key: str = Field(pattern=r"^(summary|role)$")
    en: str = Field(max_length=1200, pattern=TEXT)
    fr: str = Field(max_length=1200, pattern=TEXT)


@app.post("/api/resume/profile")
def api_resume_profile(body: ProfileVersion):
    """A new version of the summary or the role (the old ones are kept): src/master.py set summary|role; a summary
    version is then reviewed (src/score_summary.py, through master.py's scoring hook)."""
    return script_result(run_script("src/master.py", "set", body.key, body.en, body.fr))


class Rescore(BaseModel):
    id: int


@app.post("/api/resume/rescore")
def api_resume_rescore(body: Rescore):
    """Score one candidate again with the bullet rubric: src/score_bullet.py rescore."""
    return script_result(run_script("src/score_bullet.py", "rescore", str(body.id), timeout=320))


@app.post("/api/resume/summary/rescore")
def api_resume_summary_rescore(body: Rescore):
    """Review one summary version again with the Name / Fame / Aim prompt: src/score_summary.py rescore <id>."""
    return script_result(run_script("src/score_summary.py", "rescore", str(body.id), timeout=320))


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
