"""Offers and compositions live in data/resume.db only. This is the one way in and out.

An offer is the job posting (company, title, link, posting text, location) with its requirements: the keywords
it asks for, each with a priority (100 must-have, 0 preferred) and an optional min_years. A composition is one
composed resume in a job folder (jobs/<slug>-vN), usually for an offer; several compositions can share an offer.

load(folder) returns the job dict the pipeline works with:
  title ("Company — Title"), posting_text, pdf_name, company (slug), url, location, french_version, sent,
  skipped_terms, created_at, offer_id, requirements [{id: R01, section, priority, quote, description,
  terms, targets, reviewed[, kind, min_years]}]
Requirements are rebuilt from the db on every load (one per keyword, its min_years included; R01... are positions): the posting quote is not
stored, so quote is empty and description is the keyword. save(folder, data) writes a job dict back.

Usage: python3 src/offers.py sent jobs/<slug> [YYYY-MM-DD]   # mark a job as sent (default today); it is then frozen
       python3 src/offers.py note jobs/<slug> "<keyword>" ["text"]   # interview note on one of its offer's requirements
                                                                     # (no text: delete it); fine on a sent job
"""

import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

import db
import paths
from db import i18n, tr

TARGETS = {"programming_language": ["skills", "experience"], "technology": ["skills", "experience"],
           "technical": ["skills", "experience"], "design": ["skills", "experience"], "ai": ["skills", "experience"],
           "soft": ["experience"], "language": ["summary"], "location": ["summary"], "education": ["summary"]}
DEGREE = re.compile(r"\b(bachelor|master|degree|diploma|bac\s*\+|licence|ingénieur|engineering school)", re.I)


def _folder_key(folder: Path) -> str:
    return f"jobs/{Path(folder).name}"


def slugify(text: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")


def english_mentioned(posting: str) -> bool:
    return bool(re.search(r"\b(anglais|english)\b", posting, re.I))


def posting_language(posting: str) -> str:
    from build_fr import ENGLISH_WORDS, FRENCH_WORDS  # late: build_fr imports build_resume, which imports this module
    return "fr" if len(FRENCH_WORDS.findall(posting)) > 2 * len(ENGLISH_WORDS.findall(posting)) else "en"


def composition(folder: Path, con) -> "db.sqlite3.Row | None":
    return con.execute("SELECT * FROM compositions WHERE folder = ?", (_folder_key(folder),)).fetchone()


def exists(folder: Path, con=None) -> bool:
    con = con or db.connect()
    return composition(folder, con) is not None


def company_id(con, name: str) -> int:
    row = con.execute(f"SELECT id FROM companies WHERE lower({db.EN.format('name')}) = lower(?)", (name.strip(),)).fetchone()
    return row[0] if row else con.execute("INSERT INTO companies (name) VALUES (?)", (i18n(name.strip()),)).lastrowid


def load(folder: Path, con=None) -> dict:
    con = con or db.connect()
    comp = composition(folder, con)
    if comp is None:
        raise FileNotFoundError(f"No composition for {Path(folder).name} in data/resume.db")
    job = {"pdf_name": comp["pdf_name"], "sent": comp["sent_at"],
           "created_at": comp["created_at"], "requirements": []}
    offer = con.execute("SELECT o.*, c.name AS company_name FROM offers o JOIN companies c ON c.id = o.company_id "
                        "WHERE o.id = ?", (comp["offer_id"],)).fetchone() if comp["offer_id"] else None
    if offer is None:
        job["title"] = Path(folder).name
        return {k: v for k, v in job.items() if v is not None}
    company = tr(offer["company_name"])
    loc = con.execute("SELECT city, country FROM locations WHERE id = ?", (offer["location_id"],)).fetchone()
    job.update({"title": f"{company} — {offer['title']}", "posting_text": offer["posting"], "company": slugify(company),
                "url": offer["link"], "location": f"{tr(loc['city'])}, {tr(loc['country'])}" if loc else None,
                "french_version": offer["language"] == "fr" and not offer["english_mentioned"],
                "skipped_terms": json.loads(offer["skipped_terms"] or "{}"), "offer_id": offer["id"]})
    rows = con.execute("SELECT r.priority, r.min_years, k.keyword, s.type FROM requirements r "
                       "JOIN skill_keywords k ON k.id = r.keyword_id JOIN skills s ON s.id = k.skill_id "
                       "WHERE r.offer_id = ? AND NOT s.ignored ORDER BY r.priority DESC, r.id", (offer["id"],)).fetchall()
    for r in rows:  # one requirement per keyword; the years it asks for are part of it, never a second requirement
        job["requirements"].append({
            "section": "location" if r["type"] == "location" else "requirement",
            "priority": "must_have" if r["priority"] >= 50 else "preferred", "quote": "", "reviewed": True,
            "description": r["keyword"] + (f" ({r['min_years']:g}+ years)" if r["min_years"] else ""),
            "terms": [r["keyword"]], "targets": TARGETS.get(r["type"], ["skills", "experience"]), "type": r["type"],
            **({"min_years": r["min_years"]} if r["min_years"] else {})})
    for i, req in enumerate(job["requirements"], 1):
        req["id"] = f"R{i:02d}"
    return {k: v for k, v in job.items() if v not in (None, {}) or k == "requirements"}


def save(folder: Path, job: dict, con=None) -> int:
    """Create or update the folder's composition and its offer (job["offer_id"] reuses an existing offer, as a new
    version does). The offer's requirements are replaced, except while this composition is sent."""
    own = con is None
    con = con or db.connect()
    comp = composition(folder, con)
    name, _, title = job["title"].partition(" — ")
    oid = job.get("offer_id") or (comp and comp["offer_id"])
    if title:  # "Company — Title": a composition for an offer
        posting = job.get("posting_text") or ""
        import master  # late: master imports db_sync, which imports this module
        fields = {"company_id": company_id(con, name), "title": title, "link": job.get("url"), "posting": posting,
                  "language": posting_language(posting), "english_mentioned": int(english_mentioned(posting)),
                  "location_id": master.location_id(con, job.get("location")),
                  "skipped_terms": json.dumps(job.get("skipped_terms") or {}, ensure_ascii=False)}
        if oid:
            con.execute(f"UPDATE offers SET {', '.join(f'{k} = ?' for k in fields)} WHERE id = ?", (*fields.values(), oid))
        else:
            oid = con.execute(f"INSERT INTO offers ({', '.join(fields)}) VALUES ({', '.join('?' * len(fields))})",
                              tuple(fields.values())).lastrowid
    was_sent = bool(comp and comp["sent_at"])
    values = (oid, job.get("pdf_name", "resume.pdf"), job.get("sent"))
    if comp:
        con.execute("UPDATE compositions SET offer_id = ?, pdf_name = ?, sent_at = ?, "
                    "updated_at = datetime('now') WHERE id = ?", (*values, comp["id"]))
    else:
        con.execute("INSERT INTO compositions (offer_id, pdf_name, sent_at, folder) VALUES (?, ?, ?, ?)",
                    (*values, _folder_key(folder)))
    if oid and not was_sent and "requirements" in job:
        save_requirements(con, oid, job["requirements"])
    if own:
        con.commit()
        db.dump(con)
    return oid or 0


def from_parsed(parsed: dict) -> list[dict]:
    """src/parse_offer.py's output -> requirement dicts for save(): one per skill the posting asks for (type 'none'
    is skipped), with its type, priority (100 / 0) and min_years."""
    out = []
    for phrase in parsed.get("phrases", []):
        for s in phrase.get("skills", []):
            if s.get("type") in (None, "none"):
                continue
            out.append({"terms": [s["name"]], "type": s["type"], "quote": phrase["text"],
                        "section": "location" if s["type"] == "location" else "requirement",
                        "priority": "must_have" if (s.get("priority") or 0) >= 50 else "preferred",
                        **({"kind": "years_experience", "min_years": s["min_years"]} if s.get("min_years") else {})})
    where = parsed_location(parsed) or ""
    city = (where.rpartition(",")[0] or where).strip()  # the offer-level location is the reliable one
    if city and not any(r["type"] == "location" for r in out):
        out.append({"terms": [city], "type": "location", "quote": parsed.get("location") or "", "section": "location",
                    "priority": "must_have"})
    return out


def parsed_location(parsed: dict) -> str | None:
    """'Berlin, Germany (hybrid)' -> 'Berlin, Germany' (the work arrangement isn't a place)."""
    return re.sub(r"\s*\([^)]*\)", "", parsed.get("location") or "").strip() or None


def save_requirements(con, offer_id: int, requirements: list[dict]) -> None:
    """Requirement dicts (terms, priority, type or section, min_years) -> one row per keyword, highest priority and
    largest min_years kept when a keyword appears twice. A years requirement attaches to its terms."""
    rows: dict[int, dict] = {}
    for r in requirements:
        kind = r.get("type") or ("location" if r.get("section") == "location" else
                                 "education" if DEGREE.search(r.get("quote", "")) else None)
        for term in r.get("terms", []):
            kid = db.keyword_id(con, term, kind=kind)
            row = rows.setdefault(kid, {"priority": 0, "min_years": None})
            row["priority"] = max(row["priority"], db.MUST_HAVE if r.get("priority") == "must_have" else 0)
            if r.get("kind") == "years_experience":
                row["min_years"] = max(row["min_years"] or 0, r["min_years"])
    # upsert, never delete-all: a kept requirement keeps its id, so its interview note (ON DELETE CASCADE) survives
    # an ignored skill's requirement is missing from load(), so a save must not delete it: un-ignoring brings it back
    con.execute(f"DELETE FROM requirements WHERE offer_id = ? AND keyword_id NOT IN ({', '.join('?' * len(rows))}) "
                "AND keyword_id NOT IN (SELECT k.id FROM skill_keywords k JOIN skills s ON s.id = k.skill_id "
                "WHERE s.ignored)", (offer_id, *rows))
    con.executemany("INSERT INTO requirements (offer_id, keyword_id, priority, min_years) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT (offer_id, keyword_id) DO UPDATE SET priority = excluded.priority, "
                    "min_years = excluded.min_years", [(offer_id, kid, r["priority"], r["min_years"]) for kid, r in rows.items()])


def all_folders(con=None) -> list[Path]:
    con = con or db.connect()
    return [paths.ROOT / f for (f,) in con.execute("SELECT folder FROM compositions ORDER BY created_at DESC, id DESC")]


def read(arg: Path) -> dict:
    """A command-line job: jobs/<slug> (or jobs/<slug>/job.json) from the db, or an actual JSON file (fixtures)."""
    arg = Path(arg)
    if arg.suffix == ".json" and arg.is_file():
        return json.loads(arg.read_text(encoding="utf-8"))
    return load(paths.folder_arg(arg))


def write(arg: Path, job: dict) -> None:
    """Save where read() found it: back to the JSON file, or to the db."""
    arg = Path(arg)
    if arg.suffix == ".json" and arg.is_file():
        arg.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        save(paths.folder_arg(arg), job)


def mark_sent(folder: Path, when: str | None = None) -> str:
    """Record the day the job was sent: from then on it is frozen (no rebuild, edit or republish)."""
    con = db.connect()
    comp = composition(folder, con)
    if comp["sent_at"]:
        sys.exit(f"{Path(folder).name} was already sent on {comp['sent_at']}")
    day = date.fromisoformat(when) if when else date.today()
    if day > date.today():
        sys.exit(f"{day} is in the future")
    con.execute("UPDATE compositions SET sent_at = ?, updated_at = datetime('now') WHERE id = ?", (day.isoformat(), comp["id"]))
    con.commit()
    db.dump(con)
    return day.isoformat()


def save_note(folder: Path, keyword: str, text: str = "") -> str:
    """The interview note of one requirement (offer + keyword): set, or deleted when empty. Notes live in the db only,
    on the offer's requirement, so every version of the job shows them and a sent folder is never touched."""
    con = db.connect()
    comp = composition(folder, con)
    row = con.execute("SELECT r.id FROM requirements r JOIN skill_keywords k ON k.id = r.keyword_id "
                      "WHERE r.offer_id = ? AND k.keyword = ?", (comp["offer_id"], keyword.strip().lower())).fetchone()
    if row is None:
        sys.exit(f"'{keyword}' is not a requirement of {Path(folder).name}")
    if text.strip():
        con.execute("INSERT INTO interview_notes (requirement_id, note) VALUES (?, ?) ON CONFLICT (requirement_id) "
                    "DO UPDATE SET note = excluded.note, updated_at = datetime('now')", (row[0], text.strip()))
    else:
        con.execute("DELETE FROM interview_notes WHERE requirement_id = ?", (row[0],))
    con.commit()
    db.dump(con)
    return "saved" if text.strip() else "deleted"


def main() -> None:
    if len(sys.argv) in (4, 5) and sys.argv[1] == "note":
        folder = paths.folder_arg(Path(sys.argv[2]))
        if not exists(folder):
            sys.exit(f"No composition for {folder.name} in data/resume.db")
        print(f"Note on '{sys.argv[3]}' {save_note(folder, sys.argv[3], sys.argv[4] if len(sys.argv) == 5 else '')}")
        return
    if len(sys.argv) not in (3, 4) or sys.argv[1] != "sent":
        sys.exit(__doc__)
    folder = paths.folder_arg(Path(sys.argv[2]))
    if not exists(folder):
        sys.exit(f"No composition for {folder.name} in data/resume.db")
    try:
        day = mark_sent(folder, sys.argv[3] if len(sys.argv) == 4 else None)
    except ValueError:
        sys.exit(f"Not a date: {sys.argv[3]} (use YYYY-MM-DD)")
    print(f"Marked {folder.name} as sent on {day}")


assert slugify("Y Strategie") == "y-strategie" and slugify("Théodo") == "theodo"

if __name__ == "__main__":
    main()
