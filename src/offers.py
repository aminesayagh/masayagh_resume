"""Job offers live in data/resume.db only: posting, details and requirements. This is the one way in and out.

load(folder) returns the same dict a job.json used to hold, so the rest of the pipeline is unchanged:
  title ("Company — Title"), posting_text, pdf_name, company (slug), url, location, location_match,
  french_version, sent, previous_version, template_sha, skipped_terms, requirements [{id: R01..., ...}], overrides.
save(folder, data) writes it back. Requirement ids (R01...) are positions, recomputed on every load.
"""

import json
from datetime import date
from pathlib import Path

import db
import paths


def _folder_key(folder: Path) -> str:
    return f"jobs/{Path(folder).name}"


def exists(folder: Path, con=None) -> bool:
    con = con or db.connect()
    return con.execute("SELECT 1 FROM offers WHERE folder = ?", (_folder_key(folder),)).fetchone() is not None


def load(folder: Path, con=None) -> dict:
    con = con or db.connect()
    row = con.execute("SELECT o.*, c.name AS company_name, p.folder AS previous_folder FROM offers o "
                      "JOIN companies c ON c.id = o.company_id LEFT JOIN offers p ON p.id = o.previous_offer_id "
                      "WHERE o.folder = ?", (_folder_key(folder),)).fetchone()
    if row is None:
        raise FileNotFoundError(f"No offer for {Path(folder).name} in data/resume.db")
    job = {"title": f"{row['company_name']} — {row['title']}", "posting_text": row["posting"],
           "pdf_name": row["pdf_name"], "company": row["company_slug"], "url": row["link"],
           "location": row["location"], "location_match": row["location_match"],
           "french_version": bool(row["french_version"]), "sent": row["sent_at"],
           "previous_version": row["previous_folder"].removeprefix("jobs/") if row["previous_folder"] else None,
           "template_sha": row["template_sha"], "skipped_terms": json.loads(row["skipped_terms"] or "{}"),
           "requirements": [], "overrides": []}
    for i, r in enumerate(con.execute("SELECT * FROM requirements WHERE offer_id = ? ORDER BY id", (row["id"],)), 1):
        rid = f"R{i:02d}"
        req = {"id": rid, "section": r["section"], "priority": r["priority"], "quote": r["quote"],
               "description": r["description"], "terms": [t for (t,) in con.execute(
                   "SELECT term FROM requirement_terms WHERE requirement_id = ? ORDER BY rowid", (r["id"],))],
               "reviewed": bool(r["reviewed"])}
        if r["kind"] != "evidence":
            req["kind"], req["min_years"] = r["kind"], r["min_years"]
        if r["targets"]:
            req["targets"] = r["targets"].split(",")
        if r["note"]:
            req["note"] = r["note"]
        job["requirements"].append(req)
        if r["override_status"]:
            job["overrides"].append({"id": rid, "status": r["override_status"], "reason": r["override_reason"],
                                     "pdf_quote": r["override_quote"]})
    return {k: v for k, v in job.items() if v not in (None, {}, []) or k in ("requirements", "title", "posting_text")}


def save(folder: Path, job: dict, con=None) -> int:
    """Create or update the offer. Requirements are replaced, except on an offer that was already sent."""
    own = con is None
    con = con or db.connect()
    name, _, title = job["title"].partition(" — ")
    company = con.execute("SELECT id FROM companies WHERE name = ?", (name.strip(),)).fetchone()
    company_id = company[0] if company else con.execute(
        "INSERT INTO companies (name, kind) VALUES (?, 'prospect')", (name.strip(),)).lastrowid
    posting = job.get("posting_text") or ""
    from build_fr import ENGLISH_WORDS, FRENCH_WORDS  # language of the posting itself
    language = "fr" if len(FRENCH_WORDS.findall(posting)) > 2 * len(ENGLISH_WORDS.findall(posting)) else "en"
    unreviewed = any(not r.get("reviewed") for r in job.get("requirements", []))
    status = "sent" if job.get("sent") else ("draft" if unreviewed or not job.get("requirements") else "ready")
    previous = con.execute("SELECT id FROM offers WHERE folder = ?",
                           (f"jobs/{job['previous_version']}",)).fetchone() if job.get("previous_version") else None
    fields = {"company_id": company_id, "title": title or name, "link": job.get("url"), "pdf_name": job.get("pdf_name", "resume.pdf"),
              "company_slug": job.get("company"), "language": language, "french_version": int(bool(job.get("french_version"))),
              "location": job.get("location"), "location_match": job.get("location_match"), "posting": posting,
              "status": status, "sent_at": job.get("sent"), "previous_offer_id": previous and previous[0],
              "template_sha": job.get("template_sha"), "skipped_terms": json.dumps(job.get("skipped_terms") or {}, ensure_ascii=False)}
    row = con.execute("SELECT id, status FROM offers WHERE folder = ?", (_folder_key(folder),)).fetchone()
    if row:
        oid, was_sent = row[0], row[1] == "sent"
        con.execute(f"UPDATE offers SET {', '.join(f'{k} = ?' for k in fields)} WHERE id = ?", (*fields.values(), oid))
    else:
        was_sent = False
        fields.update(folder=_folder_key(folder), created_at=job.get("created_at") or date.today().isoformat())
        oid = con.execute(f"INSERT INTO offers ({', '.join(fields)}) VALUES ({', '.join('?' * len(fields))})",
                          tuple(fields.values())).lastrowid
    if not was_sent:
        old = [r for (r,) in con.execute("SELECT id FROM requirements WHERE offer_id = ?", (oid,))]
        con.executemany("DELETE FROM requirement_terms WHERE requirement_id = ?", [(r,) for r in old])
        con.execute("DELETE FROM offer_results WHERE offer_id = ?", (oid,))
        con.execute("DELETE FROM requirements WHERE offer_id = ?", (oid,))
        overrides = {o["id"]: o for o in job.get("overrides", [])}
        for r in job.get("requirements", []):
            o = overrides.get(r["id"], {})
            rid = con.execute(
                "INSERT INTO requirements (offer_id, section, priority, quote, description, kind, min_years, targets, "
                "reviewed, note, override_status, override_reason, override_quote) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (oid, r["section"], r["priority"], r["quote"], r.get("description", ""), r.get("kind", "evidence"),
                 r.get("min_years"), ",".join(r.get("targets", [])) or None, int(bool(r.get("reviewed"))), r.get("note"),
                 o.get("status"), o.get("reason"), o.get("pdf_quote"))).lastrowid
            for t in r.get("terms", []):
                skill = con.execute("SELECT s.id FROM skills s LEFT JOIN skill_keywords k ON k.skill_id = s.id "
                                    "WHERE lower(s.name_en) = lower(?) OR lower(k.keyword) = lower(?) LIMIT 1", (t, t)).fetchone()
                con.execute("INSERT OR IGNORE INTO requirement_terms (requirement_id, term, skill_id) VALUES (?, ?, ?)",
                            (rid, t, skill and skill[0]))
    if job.get("sent") and not was_sent:
        snapshot(con, oid, folder, job["sent"])
    if own:
        con.commit()
        db.dump(con)
    return oid


def snapshot(con, offer_id: int, folder: Path, sent: str) -> None:
    """What the employer received, measured: the review's per-term results at the moment the offer is sent."""
    review = json.loads(paths.review_json(folder).read_text(encoding="utf-8")) if paths.review_json(folder).exists() else {}
    ids = [r for (r,) in con.execute("SELECT id FROM requirements WHERE offer_id = ? ORDER BY id", (offer_id,))]
    con.execute("DELETE FROM offer_results WHERE offer_id = ?", (offer_id,))
    for res in review.get("results", []):
        i = int(res["id"][1:]) - 1
        for t in res.get("terms", []) if 0 <= i < len(ids) else []:
            con.execute("INSERT INTO offer_results (offer_id, requirement_id, term, status, found_in, snapshot_at) "
                        "VALUES (?, ?, ?, ?, ?, ?)", (offer_id, ids[i], t["term"],
                                                      t["status"] if t["status"] in ("met", "partial") else "missing",
                                                      t.get("section"), sent))


def all_folders(con=None) -> list[Path]:
    con = con or db.connect()
    return [paths.ROOT / f for (f,) in con.execute("SELECT folder FROM offers ORDER BY created_at DESC, id DESC")]


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
