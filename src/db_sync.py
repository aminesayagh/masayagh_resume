#!/usr/bin/env python3
"""Grow the library from a job folder: new approved lines (in their activity) and rewritten cover paragraphs.
Called after every job build. The offer and composition themselves are written by src/offers.py.

Usage: python3 src/db_sync.py jobs/<slug>      (or import: sync_job(folder))

Records every resume line used for the job that the library doesn't know yet, as an approved line of the activity
it rewords (worked out from the composition's previous lines), and rewritten cover-letter paragraphs.
"""

import json
import re
import sys
from pathlib import Path

import db
import offers
import paths
from db import EN, i18n, tr

ROOT = db.ROOT
SAME_EXPERIENCE = {"technical consulting": "Technical Consultant",  # older resumes named it differently
                   "digital consulting": "Rich Media"}  # merged into Rich Media (Nov 2026)
PARTS = ("opening", "example", "support", "close")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def company_name(entry: dict) -> str:
    name = entry["company"].strip().rstrip(",").strip()
    return SAME_EXPERIENCE.get(name.casefold(), name)


def word_in(word: str, text: str) -> bool:
    return bool(re.search(rf"(?<![\w.]){re.escape(word)}(?![\w])", text, re.I))


def experience_ids(con) -> dict[str, int]:
    """Company name (English or French, lowercase) -> experience id."""
    out = {}
    for x, name in con.execute("SELECT e.id, c.name FROM experiences e JOIN contracts k ON k.id = e.contract_id "
                               "JOIN companies c ON c.id = k.company_id"):
        for value in json.loads(name).values():
            out[value.casefold()] = x
    return out


def skill_words(con) -> list[tuple[int, list[str]]]:
    rows = con.execute("SELECT skill_id, group_concat(keyword, '|') FROM skill_keywords WHERE lang = 'en' "
                       "GROUP BY skill_id").fetchall()
    return [(sid, kw.split("|")) for sid, kw in rows]


def link_skills(con, table: str, key: str, row_id: int, text: str) -> None:
    for sid, names in skill_words(con):
        if any(len(n) > 1 and word_in(n, text) for n in names):
            con.execute(f"INSERT OR IGNORE INTO {table} ({key}, skill_id) VALUES (?, ?)", (row_id, sid))


def line_id(con, experience_id: int, text: str) -> int | None:
    """Lines are found by exact English text within an experience: a resume never repeats a line."""
    row = con.execute(f"SELECT d.id FROM descriptions d JOIN activities a ON a.id = d.activity_id "
                      f"WHERE a.experience_id = ? AND {EN.format('d.text')} = ?", (experience_id, text)).fetchone()
    return row and row[0]


def add_line(con, activity_id: int, kind: str, text: str, text_fr: str | None = None) -> int | None:
    """A new line joins the library in that activity (returns its id; an existing identical line is reused)."""
    if not text.strip():
        return None
    x = con.execute("SELECT experience_id FROM activities WHERE id = ?", (activity_id,)).fetchone()[0]
    if found := line_id(con, x, text):
        return found
    lid = con.execute("INSERT INTO descriptions (activity_id, kind, text) VALUES (?, ?, ?)",
                      (activity_id, kind, i18n(text, text_fr))).lastrowid
    link_skills(con, "description_skills", "description_id", lid, text)
    return lid


def new_activity(con, experience_id: int, text: str) -> int:
    """A line that rewords no known line gets its own activity, inactive until reviewed (so it never adds a bullet
    to other resumes by itself)."""
    order = con.execute("SELECT coalesce(max(sort_order), 0) + 1 FROM activities WHERE experience_id = ?",
                        (experience_id,)).fetchone()[0]
    print(f"db_sync: new activity (inactive, review it in the library) for: {text[:60]}…")
    return con.execute("INSERT INTO activities (experience_id, label, sort_order, active) VALUES (?, ?, ?, 0)",
                       (experience_id, " ".join(text.split()[:5]), order)).lastrowid


def sync_lines(con, previous: list[int], experience_id: int, lines: list[tuple[str, str]]) -> list[int]:
    """The library ids of one experience's lines as used now. A line the library doesn't know joins the activity
    of the line it replaced: the one of this experience used at the previous build that is gone now (by position
    when several changed at once). Otherwise it gets a new, inactive activity."""
    known = [line_id(con, experience_id, text) for _, text in lines]
    gone = {pos: d for pos, d in enumerate(previous) if d not in known}
    new = [pos for pos, d in enumerate(known) if d is None]
    for pos in new:
        kind, text = lines[pos]
        replaced = (list(gone.values()) if len(gone) == 1 and len(new) == 1 else [gone[pos]] if pos in gone else [])
        activity = con.execute("SELECT activity_id FROM descriptions WHERE id = ?", (replaced[0],)).fetchone()[0] \
            if len(replaced) == 1 else new_activity(con, experience_id, text)
        known[pos] = add_line(con, activity, kind, text)
    return known


def default_paragraphs(con, lang: str = "en") -> list[str]:
    """The default letter: the newest approved paragraph of each part (opening, example, support, close)."""
    out = []
    for part in PARTS:
        row = con.execute("SELECT text FROM cover_paragraphs WHERE part = ? AND status = 'approved' "
                          "ORDER BY created_at DESC, id DESC LIMIT 1", (part,)).fetchone()
        if row:
            out.append(tr(row[0], lang))
    return out


def sync_job(folder: Path, con=None) -> int | None:
    own = con is None
    con = con or db.connect()
    folder = folder.resolve()
    comp = offers.composition(folder, con)
    if comp is None:
        return None
    job, content = offers.load(folder, con), load(paths.content(folder))
    name, _, title = job["title"].partition(" — ")
    experiences = experience_ids(con)
    previous = [d for (d,) in con.execute("SELECT description_id FROM offer_lines WHERE composition_id = ? "
                                          "ORDER BY position", (comp["id"],))]
    used: list[int] = []
    for e in content.get("experience", []):  # the JSON is read as text only; the db works out the rest
        if (x := experiences.get(company_name(e).casefold())) is None:
            print(f"db_sync: no experience '{company_name(e)}' in the library; its lines were not recorded.")
            continue
        mine = [d for d in previous if line_experience(con, d) == x]
        used += sync_lines(con, mine, x, ([("description", e["description"])] if e.get("description") else [])
                           + [("bullet", b) for b in e.get("bullets", [])])
    con.execute("DELETE FROM offer_lines WHERE composition_id = ?", (comp["id"],))
    con.executemany("INSERT INTO offer_lines VALUES (?, ?, ?)", [(comp["id"], p, d) for p, d in enumerate(used) if d])

    filled = [t.replace("{company}", name.strip()).replace("{job_title}", title or name) for t in default_paragraphs(con)]
    letter, letter_fr = load(paths.cover(folder)), load(paths.cover(folder, "fr"))
    paragraphs = letter.get("paragraphs", [])
    for i, text in enumerate(paragraphs):
        if text in filled or con.execute(f"SELECT 1 FROM cover_paragraphs WHERE {EN.format('text')} = ?", (text,)).fetchone():
            continue  # the default letter (stored once, with its placeholders) or a paragraph already known
        part = "opening" if i == 0 else "close" if i == len(paragraphs) - 1 else "example" if i == 1 else "support"
        text_fr = (letter_fr.get("paragraphs") or [None] * len(paragraphs))[i] if letter_fr else None
        pid = con.execute("INSERT INTO cover_paragraphs (part, text) VALUES (?, ?)", (part, i18n(text, text_fr))).lastrowid
        link_skills(con, "cover_paragraph_skills", "paragraph_id", pid, text)
        for name_, x in experiences.items():
            if name_ != "freelance" and word_in(name_, text):
                con.execute("INSERT OR IGNORE INTO cover_paragraph_experiences VALUES (?, ?)", (pid, x))
    if own:
        con.commit()
        db.dump(con)
    return comp["id"]


def line_experience(con, description_id: int) -> int | None:
    row = con.execute("SELECT a.experience_id FROM descriptions d JOIN activities a ON a.id = d.activity_id "
                      "WHERE d.id = ?", (description_id,)).fetchone()
    return row and row[0]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(f"Synced composition {sync_job(Path(sys.argv[1]))}")
