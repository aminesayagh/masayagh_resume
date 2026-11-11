#!/usr/bin/env python3
"""The resume knowledge base: experiences and their approved lines, skills and keywords, offers.

Usage:
  python3 src/db.py dump      # write data/resume.sql (text, committed to git) from data/resume.db
  python3 src/db.py restore   # rebuild data/resume.db from data/resume.sql (after a git pull)

data/resume.db is local and ignored by git; data/resume.sql is the reviewable copy. Job folders keep their
files (posting, content.json snapshot, PDFs, reports); the database holds what is reused across jobs.
"""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "resume.db"
DUMP = ROOT / "data" / "resume.sql"

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('employer', 'prospect')),
  international INTEGER NOT NULL DEFAULT 0,
  country TEXT
);
CREATE TABLE IF NOT EXISTS contact (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  phone_link TEXT NOT NULL,
  location_en TEXT NOT NULL,
  location_fr TEXT,
  website TEXT NOT NULL,
  website_link TEXT NOT NULL,
  github TEXT,
  linkedin TEXT
);
CREATE TABLE IF NOT EXISTS skill_layout (
  row INTEGER NOT NULL,
  position INTEGER NOT NULL,
  label_en TEXT NOT NULL,
  label_fr TEXT,
  PRIMARY KEY (row, position)
);
CREATE TABLE IF NOT EXISTS languages (
  id INTEGER PRIMARY KEY,
  sort_order INTEGER NOT NULL,
  name_en TEXT NOT NULL,
  name_fr TEXT,
  level_en TEXT NOT NULL,
  level_fr TEXT
);
CREATE TABLE IF NOT EXISTS experiences (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  role TEXT NOT NULL,
  detail TEXT,
  location TEXT,
  type TEXT NOT NULL CHECK (type IN ('job', 'freelance')),
  start_at TEXT NOT NULL,
  end_at TEXT,
  sort_order INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS activities (
  id INTEGER PRIMARY KEY,
  experience_id INTEGER NOT NULL REFERENCES experiences(id),
  label TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS descriptions (
  id INTEGER PRIMARY KEY,
  experience_id INTEGER NOT NULL REFERENCES experiences(id),
  activity_id INTEGER REFERENCES activities(id),
  kind TEXT NOT NULL CHECK (kind IN ('description', 'bullet')),
  text_en TEXT NOT NULL,
  text_fr TEXT,
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  first_offer_id INTEGER REFERENCES offers(id),
  created_at TEXT NOT NULL DEFAULT (date('now')),
  UNIQUE (experience_id, text_en)
);
CREATE TABLE IF NOT EXISTS description_skills (
  description_id INTEGER NOT NULL REFERENCES descriptions(id),
  skill_id INTEGER NOT NULL REFERENCES skills(id),
  PRIMARY KEY (description_id, skill_id)
);
CREATE TABLE IF NOT EXISTS cover_paragraphs (
  id INTEGER PRIMARY KEY,
  part TEXT NOT NULL CHECK (part IN ('opening', 'example', 'support', 'close')),
  text_en TEXT NOT NULL UNIQUE,
  text_fr TEXT,
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  first_offer_id INTEGER REFERENCES offers(id),
  created_at TEXT NOT NULL DEFAULT (date('now'))
);
CREATE TABLE IF NOT EXISTS cover_paragraph_experiences (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id),
  experience_id INTEGER NOT NULL REFERENCES experiences(id),
  PRIMARY KEY (paragraph_id, experience_id)
);
CREATE TABLE IF NOT EXISTS cover_paragraph_skills (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id),
  skill_id INTEGER NOT NULL REFERENCES skills(id),
  PRIMARY KEY (paragraph_id, skill_id)
);
CREATE TABLE IF NOT EXISTS skills (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('technical', 'soft', 'language', 'location', 'design', 'ai')),
  name_en TEXT NOT NULL UNIQUE,
  name_fr TEXT,
  start_at TEXT,
  end_at TEXT
);
CREATE TABLE IF NOT EXISTS skill_keywords (
  skill_id INTEGER NOT NULL REFERENCES skills(id),
  keyword TEXT NOT NULL,
  lang TEXT NOT NULL CHECK (lang IN ('en', 'fr')),
  PRIMARY KEY (keyword, lang)
);
CREATE TABLE IF NOT EXISTS profile (
  id INTEGER PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  text_en TEXT NOT NULL,
  text_fr TEXT
);
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  tech TEXT NOT NULL,
  link TEXT NOT NULL,
  duration TEXT NOT NULL,
  duration_fr TEXT
);
CREATE TABLE IF NOT EXISTS education (
  id INTEGER PRIMARY KEY,
  degree_en TEXT NOT NULL,
  degree_fr TEXT,
  institution_en TEXT NOT NULL,
  institution_fr TEXT,
  start_at TEXT NOT NULL,
  end_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS certifications (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  issuer TEXT NOT NULL,
  link TEXT NOT NULL,
  date TEXT
);
CREATE TABLE IF NOT EXISTS offers (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  title TEXT NOT NULL,
  link TEXT,
  folder TEXT NOT NULL UNIQUE,
  pdf_name TEXT NOT NULL,
  resume_url TEXT,
  cover_letter_url TEXT,
  published_at TEXT,
  language TEXT NOT NULL CHECK (language IN ('en', 'fr')),
  french_version INTEGER NOT NULL DEFAULT 0,
  location TEXT,
  location_match TEXT,
  posting TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft', 'ready', 'sent')),
  created_at TEXT NOT NULL,
  sent_at TEXT,
  previous_offer_id INTEGER REFERENCES offers(id),
  company_slug TEXT,
  template_sha TEXT,
  skipped_terms TEXT
);
CREATE TABLE IF NOT EXISTS requirements (
  id INTEGER PRIMARY KEY,
  offer_id INTEGER NOT NULL REFERENCES offers(id),
  section TEXT NOT NULL,
  priority TEXT NOT NULL CHECK (priority IN ('must_have', 'preferred')),
  quote TEXT NOT NULL,
  description TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('evidence', 'years_experience')),
  min_years REAL,
  targets TEXT,
  reviewed INTEGER NOT NULL DEFAULT 0,
  note TEXT,
  override_status TEXT,
  override_reason TEXT,
  override_quote TEXT
);
CREATE TABLE IF NOT EXISTS requirement_terms (
  requirement_id INTEGER NOT NULL REFERENCES requirements(id),
  term TEXT NOT NULL,
  skill_id INTEGER REFERENCES skills(id),
  PRIMARY KEY (requirement_id, term)
);
CREATE TABLE IF NOT EXISTS offer_results (
  offer_id INTEGER NOT NULL REFERENCES offers(id),
  requirement_id INTEGER NOT NULL REFERENCES requirements(id),
  term TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('met', 'partial', 'missing')),
  found_in TEXT,
  description_id INTEGER REFERENCES descriptions(id),
  snapshot_at TEXT NOT NULL
);
"""


def connect(path: Path | None = None, empty: bool = False) -> sqlite3.Connection:
    """empty=True: start from no data; otherwise a missing db is rebuilt from data/resume.sql.
    DB and DUMP are read at call time, so tests can point them at a temporary database."""
    path = path or DB
    path.parent.mkdir(parents=True, exist_ok=True)
    if empty:
        path.unlink(missing_ok=True)
    elif path == DB and not DB.exists() and DUMP.exists():  # fresh clone: rebuild from the committed text copy
        restore()
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    for table, column, kind in (("descriptions", "activity_id", "INTEGER REFERENCES activities(id)"),
                                ("experiences", "company_fr", "TEXT"), ("experiences", "role_fr", "TEXT"),
                                ("experiences", "detail_fr", "TEXT"), ("projects", "tech_fr", "TEXT"),
                                ("activities", "master_id", "INTEGER REFERENCES descriptions(id)"),
                                ("cover_paragraphs", "default_order", "INTEGER"),
                                ("offers", "company_slug", "TEXT"), ("offers", "template_sha", "TEXT"),
                                ("offers", "skipped_terms", "TEXT"), ("requirements", "override_quote", "TEXT")):
        if column not in [c[1] for c in con.execute(f"PRAGMA table_info({table})")]:  # databases made before it
            con.execute(f"ALTER TABLE {table} ADD COLUMN {column} {kind}")
    sql = con.execute("SELECT sql FROM sqlite_master WHERE name = 'profile'").fetchone()[0]
    if "CHECK (key IN" in sql:  # profile once allowed only summary/role; it now also holds the cover greeting/closing
        con.executescript("ALTER TABLE profile RENAME TO profile_old;"
                          "CREATE TABLE profile (id INTEGER PRIMARY KEY, key TEXT NOT NULL UNIQUE, text_en TEXT NOT NULL, text_fr TEXT);"
                          "INSERT INTO profile SELECT * FROM profile_old; DROP TABLE profile_old;")
    return con


def aliases(con: sqlite3.Connection | None = None) -> dict[str, list[str]]:
    """Posting word -> the English words a resume may use for the same skill (name and English keywords).
    Replaces src/aliases.json: one skill row with its keywords is one set of true synonyms."""
    con = con or connect()
    out: dict[str, list[str]] = {}
    for sid, name in con.execute("SELECT id, name_en FROM skills"):
        rows = con.execute("SELECT keyword, lang FROM skill_keywords WHERE skill_id = ?", (sid,)).fetchall()
        english = [name] + [k for k, lang in rows if lang == "en"]
        for word in [name] + [k for k, _ in rows]:
            others = [w for w in english if w.casefold() != word.casefold()]
            if others:
                out.setdefault(word, [])
                out[word] += [w for w in others if w not in out[word]]
    return out


def dump(con: sqlite3.Connection | None = None) -> Path:
    con = con or connect()
    DUMP.write_text("\n".join(con.iterdump()) + "\n", encoding="utf-8")
    return DUMP


def restore() -> Path:
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(DUMP.read_text(encoding="utf-8"))
    con.close()
    return DB


if __name__ == "__main__":
    if sys.argv[1:] == ["dump"]:
        print(f"Wrote {dump()}")
    elif sys.argv[1:] == ["restore"]:
        print(f"Rebuilt {restore()} from {DUMP.name}")
    else:
        sys.exit(__doc__)
