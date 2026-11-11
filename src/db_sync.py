#!/usr/bin/env python3
"""Keep data/resume.db in step with a job folder. Called after every job build and when a job is marked sent.

Usage: python3 src/db_sync.py jobs/<slug>      (or import: sync_job(folder))

Records the offer and its requirements, every resume line used for the job that the library doesn't know yet
(as an approved line of that experience, first used by this offer), rewritten cover-letter paragraphs, and,
once the job is sent, a snapshot of its results. Sent offers keep their requirements as they were.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import build_fr
import config
import db

ROOT = db.ROOT
SAME_EXPERIENCE = {"technical consulting": "Technical Consultant",  # older resumes named it differently
                   "digital consulting": "Rich Media"}  # merged into Rich Media (Nov 2026)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def company_name(entry: dict) -> str:
    name = entry["company"].strip().rstrip(",").strip()
    return SAME_EXPERIENCE.get(name.casefold(), name)


def word_in(word: str, text: str) -> bool:
    return bool(re.search(rf"(?<![\w.]){re.escape(word)}(?![\w])", text, re.I))


def company(con, name: str, kind: str) -> int:
    row = con.execute("SELECT id FROM companies WHERE name = ?", (name,)).fetchone()
    return row[0] if row else con.execute("INSERT INTO companies (name, kind) VALUES (?, ?)", (name, kind)).lastrowid


def skill_words(con) -> list[tuple[int, list[str]]]:
    rows = con.execute("SELECT s.id, s.name_en, group_concat(k.keyword, '|') FROM skills s "
                       "LEFT JOIN skill_keywords k ON k.skill_id = s.id AND k.lang = 'en' GROUP BY s.id").fetchall()
    return [(sid, [name] + (kw.split("|") if kw else [])) for sid, name, kw in rows]


def link_skills(con, table: str, key: str, row_id: int, text: str) -> None:
    for sid, names in skill_words(con):
        if any(len(n) > 1 and word_in(n, text) for n in names):
            con.execute(f"INSERT OR IGNORE INTO {table} ({key}, skill_id) VALUES (?, ?)", (row_id, sid))


def add_line(con, experience_id: int, kind: str, text: str, offer_id: int | None, text_fr: str | None = None) -> None:
    if not text.strip():
        return
    cur = con.execute("INSERT OR IGNORE INTO descriptions (experience_id, kind, text_en, text_fr, first_offer_id) "
                      "VALUES (?, ?, ?, ?, ?)", (experience_id, kind, text, text_fr, offer_id))
    if cur.rowcount:
        link_skills(con, "description_skills", "description_id", cur.lastrowid, text)


def sync_template(con=None) -> None:
    """New lines in template/content/default.json (and their French in default-fr.json) join the library."""
    own = con is None
    con = con or db.connect()
    en, fr = load(ROOT / "template/content/default.json"), load(ROOT / "template/content/default-fr.json")
    ids = {name: x for x, name in con.execute("SELECT e.id, c.name FROM experiences e JOIN companies c ON c.id = e.company_id")}
    for e, ef in zip(en.get("experience", []), fr.get("experience", []) or [{}] * len(en.get("experience", []))):
        if (x := ids.get(company_name(e))) is None:
            print(f"db_sync: '{company_name(e)}' is not in the library yet; add the experience first.")
            continue
        add_line(con, x, "description", e.get("description", ""), None, ef.get("description"))
        for i, b in enumerate(e.get("bullets", [])):
            add_line(con, x, "bullet", b, None, (ef.get("bullets") or [None] * (i + 1))[i] if ef else None)
    for key in ("summary", "role"):
        con.execute("UPDATE profile SET text_en = ?, text_fr = ? WHERE key = ?", (en[key], fr.get(key), key))
    if own:
        con.commit()
        db.dump(con)


TEST_FIXTURES = {"fictional-full-stack-v1"}  # the test job is not a real offer


def sync_job(folder: Path, con=None) -> int | None:
    if folder.resolve().name in TEST_FIXTURES:
        return None
    own = con is None
    con = con or db.connect()
    folder = folder.resolve()
    job, review, content = load(folder / "job.json"), load(folder / "review.json"), load(folder / "content.json")
    name, _, title = job["title"].partition(" — ")
    posting = (folder / "posting.txt").read_text(encoding="utf-8")
    pdf = job.get("pdf_name", "resume.pdf")
    version = int(m[1]) if (m := re.search(r"-v(\d+)$", folder.name)) else 1
    url = config.public_url(job.get("company", ""), version, pdf)  # None when publishing is off (config.json)
    unreviewed = any(not r.get("reviewed") for r in job.get("requirements", []))
    status = "sent" if job.get("sent") else ("draft" if unreviewed or not job.get("requirements") else "ready")
    french = len(build_fr.FRENCH_WORDS.findall(posting)) > 2 * len(build_fr.ENGLISH_WORDS.findall(posting))
    previous = con.execute("SELECT id FROM offers WHERE folder = ?", (f"jobs/{job.get('previous_version')}",)).fetchone()
    values = (company(con, name.strip(), "prospect"), title or name, job.get("url"), pdf, url,
              "fr" if french else "en", int(bool(job.get("french_version"))), job.get("location"),
              job.get("location_match"), posting, status, job.get("sent"), previous and previous[0])
    row = con.execute("SELECT id, status FROM offers WHERE folder = ?", (f"jobs/{folder.name}",)).fetchone()
    if row:
        oid, was_sent = row[0], row[1] == "sent"
        con.execute("UPDATE offers SET company_id=?, title=?, link=?, pdf_name=?, resume_url=?, language=?, "
                    "french_version=?, location=?, location_match=?, posting=?, status=?, sent_at=?, "
                    "previous_offer_id=? WHERE id=?", (*values, oid))
    else:
        was_sent = False
        oid = con.execute(
            "INSERT INTO offers (company_id, title, link, pdf_name, resume_url, language, french_version, location, "
            "location_match, posting, status, sent_at, previous_offer_id, folder, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (*values, f"jobs/{folder.name}", date.fromtimestamp((folder / "posting.txt").stat().st_mtime).isoformat())).lastrowid

    if not was_sent:  # requirements of a sent offer stay as they were sent
        old = [r for (r,) in con.execute("SELECT id FROM requirements WHERE offer_id = ?", (oid,))]
        con.executemany("DELETE FROM requirement_terms WHERE requirement_id = ?", [(r,) for r in old])
        con.execute("DELETE FROM offer_results WHERE offer_id = ?", (oid,))
        con.execute("DELETE FROM requirements WHERE offer_id = ?", (oid,))
        overrides = {o["id"]: o for o in job.get("overrides", [])}
        codes = {}
        for r in job.get("requirements", []):
            o = overrides.get(r["id"], {})
            codes[r["id"]] = rid = con.execute(
                "INSERT INTO requirements (offer_id, section, priority, quote, description, kind, min_years, targets, "
                "reviewed, note, override_status, override_reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (oid, r["section"], r["priority"], r["quote"], r.get("description", ""), r.get("kind", "evidence"),
                 r.get("min_years"), ",".join(r.get("targets", [])) or None, int(bool(r.get("reviewed"))), r.get("note"),
                 o.get("status"), o.get("reason"))).lastrowid
            for t in r.get("terms", []):
                skill = con.execute("SELECT s.id FROM skills s LEFT JOIN skill_keywords k ON k.skill_id = s.id "
                                    "WHERE lower(s.name_en) = lower(?) OR lower(k.keyword) = lower(?) LIMIT 1", (t, t)).fetchone()
                con.execute("INSERT OR IGNORE INTO requirement_terms (requirement_id, term, skill_id) VALUES (?, ?, ?)",
                            (rid, t, skill and skill[0]))
        if job.get("sent"):  # just sent: keep what the employer received, measured
            for res in review.get("results", []):
                for t in res.get("terms", []):
                    if res["id"] in codes:
                        con.execute("INSERT INTO offer_results (offer_id, requirement_id, term, status, found_in, "
                                    "snapshot_at) VALUES (?, ?, ?, ?, ?, ?)",
                                    (oid, codes[res["id"]], t["term"],
                                     t["status"] if t["status"] in ("met", "partial") else "missing",
                                     t.get("section"), job["sent"]))

    experiences: dict[str, int] = {}  # company name (and product, e.g. "Hypeo") -> experience id
    for x, name_, detail in con.execute("SELECT e.id, c.name, e.detail FROM experiences e "
                                        "JOIN companies c ON c.id = e.company_id"):
        experiences[name_] = x
        if detail and detail.startswith("-"):
            experiences[detail.strip("- ").split(",")[0]] = x
    for e in content.get("experience", []):  # lines approved for this job join the library
        if (x := experiences.get(company_name(e))) is None:
            print(f"db_sync: no experience '{company_name(e)}' in the library; its lines were not recorded.")
            continue
        add_line(con, x, "description", e.get("description", ""), oid)
        for b in e.get("bullets", []):
            add_line(con, x, "bullet", b, oid)

    default = load(ROOT / "template/content/default-cover.json").get("paragraphs", [])
    filled = [t.replace("{company}", name.strip()).replace("{job_title}", title or name) for t in default]
    letter, letter_fr = load(folder / "cover.json"), load(folder / "cover-fr.json")
    paragraphs = letter.get("paragraphs", [])
    for i, text in enumerate(paragraphs):
        if text in filled:
            continue  # the default letter, stored once with its placeholders
        part = "opening" if i == 0 else "close" if i == len(paragraphs) - 1 else "example" if i == 1 else "support"
        text_fr = (letter_fr.get("paragraphs") or [None] * len(paragraphs))[i] if letter_fr else None
        cur = con.execute("INSERT OR IGNORE INTO cover_paragraphs (part, text_en, text_fr, first_offer_id) "
                          "VALUES (?, ?, ?, ?)", (part, text, text_fr, oid))
        if cur.rowcount:
            pid = cur.lastrowid
            link_skills(con, "cover_paragraph_skills", "paragraph_id", pid, text)
            for name_, x in experiences.items():
                if name_.casefold() != "freelance" and word_in(name_, text):
                    con.execute("INSERT OR IGNORE INTO cover_paragraph_experiences VALUES (?, ?)", (pid, x))
    if own:
        con.commit()
        db.dump(con)
    return oid


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(f"Synced offer {sync_job(Path(sys.argv[1]))}")
