#!/usr/bin/env python3
"""Grow the library from a job folder: new approved lines (in their activity) and rewritten cover paragraphs.
Called after every job build. The offer itself is written by src/offers.py.

Usage: python3 src/db_sync.py jobs/<slug>      (or import: sync_job(folder))

Records every resume line used for the job that the library doesn't know yet (as an approved line of that
experience and activity, first used by this offer) and rewritten cover-letter paragraphs.
"""

import json
import re
import sys
from pathlib import Path

import db
import offers
import paths

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


def add_line(con, experience_id: int, kind: str, text: str, offer_id: int | None, text_fr: str | None = None,
             activity_id: int | None = None) -> None:
    """A new line joins the library; activity_id says which activity it rewords (worked out by sync_lines)."""
    if not text.strip():
        return
    cur = con.execute("INSERT OR IGNORE INTO descriptions (experience_id, activity_id, kind, text_en, text_fr, "
                      "first_offer_id) VALUES (?, ?, ?, ?, ?, ?)", (experience_id, activity_id, kind, text, text_fr, offer_id))
    if cur.rowcount:
        link_skills(con, "description_skills", "description_id", cur.lastrowid, text)


def line_id(con, experience_id: int, text: str) -> int | None:
    """Lines are found by exact text: a resume never repeats a line."""
    row = con.execute("SELECT id FROM descriptions WHERE experience_id = ? AND text_en = ?", (experience_id, text)).fetchone()
    return row and row[0]


def sync_lines(con, offer_id: int, experience_id: int, lines: list[tuple[str, str]]) -> None:
    """Record the lines this offer uses now. A line the library doesn't know joins the activity of the line it
    replaced: the one used at the previous build that is gone now (by position when several changed at once).
    If that can't be told, it is saved without an activity and reported, never guessed."""
    previous = dict(con.execute("SELECT position, description_id FROM offer_lines WHERE offer_id = ? AND experience_id = ?",
                                (offer_id, experience_id)).fetchall())
    known = {pos: line_id(con, experience_id, text) for pos, (_, text) in enumerate(lines)}
    gone = {pos: d for pos, d in previous.items() if d not in known.values()}
    new = [pos for pos, d in known.items() if d is None]
    for pos in new:
        kind, text = lines[pos]
        replaced = (list(gone.values()) if len(gone) == 1 and len(new) == 1 else [gone[pos]] if pos in gone else [])
        activity = con.execute("SELECT activity_id FROM descriptions WHERE id = ?", (replaced[0],)).fetchone()[0] \
            if len(replaced) == 1 else None
        add_line(con, experience_id, kind, text, offer_id, activity_id=activity)
        known[pos] = line_id(con, experience_id, text)
        if activity is None:
            print(f"db_sync: new line saved without an activity (attach it when reviewing the library): {text[:60]}…")
    con.execute("DELETE FROM offer_lines WHERE offer_id = ? AND experience_id = ?", (offer_id, experience_id))
    con.executemany("INSERT INTO offer_lines VALUES (?, ?, ?, ?)", [(offer_id, experience_id, p, d) for p, d in known.items()])


def sync_job(folder: Path, con=None) -> int | None:
    own = con is None
    con = con or db.connect()
    folder = folder.resolve()
    if not offers.exists(folder, con):
        return None
    job, content = offers.load(folder, con), load(paths.content(folder))
    name, _, title = job["title"].partition(" — ")
    oid = con.execute("SELECT id FROM offers WHERE folder = ?", (f"jobs/{folder.name}",)).fetchone()[0]
    experiences: dict[str, int] = {}  # company name (and product, e.g. "Hypeo") -> experience id
    for x, name_, detail in con.execute("SELECT e.id, c.name, e.detail FROM experiences e "
                                        "JOIN companies c ON c.id = e.company_id"):
        experiences[name_] = x
        if detail and detail.startswith("-"):
            experiences[detail.strip("- ").split(",")[0]] = x
    for e in content.get("experience", []):  # the JSON is read as text only; the db works out the rest
        if (x := experiences.get(company_name(e))) is None:
            print(f"db_sync: no experience '{company_name(e)}' in the library; its lines were not recorded.")
            continue
        sync_lines(con, oid, x, ([("description", e["description"])] if e.get("description") else [])
                   + [("bullet", b) for b in e.get("bullets", [])])

    default = [t for (t,) in con.execute("SELECT text_en FROM cover_paragraphs WHERE default_order IS NOT NULL "
                                        "ORDER BY default_order")]  # the default letter, with its placeholders
    filled = [t.replace("{company}", name.strip()).replace("{job_title}", title or name) for t in default]
    letter, letter_fr = load(paths.cover(folder)), load(paths.cover(folder, "fr"))
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
