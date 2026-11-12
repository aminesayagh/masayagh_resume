#!/usr/bin/env python3
"""The resume knowledge base: master resume, experience library, skills and keywords, offers and compositions.

Usage:
  python3 src/db.py dump      # write data/resume.sql (text, committed to git) from data/resume.db
  python3 src/db.py restore   # rebuild data/resume.db from data/resume.sql (after a git pull)
  python3 src/db.py reset     # start over: an empty db, then the master resume from template/content/default*.json

data/resume.db is local and ignored by git; data/resume.sql is the reviewable copy. Job folders keep their
files (content.json, cover letters, PDFs, reports); the database holds what is reused across jobs.
Text shown on a resume in several languages is one JSON column: {"en": "...", "fr": "..."} (see tr() and i18n()).
Tables named bloc_* hold the resume's blocs: the master sections (contact, profile, languages, skill layout,
education, projects, certifications) and the experience library (experiences, activities, descriptions).
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "resume.db"
DUMP = ROOT / "data" / "resume.sql"
SKILL_TYPES = ("programming_language", "technology", "technical", "design", "ai", "soft", "language", "location", "education")
HARD_TYPES = ("programming_language", "technology", "technical", "design", "ai")  # only these have start/end dates (years of experience)
MUST_HAVE = 100  # requirements.priority: 100 = must-have, 0 = preferred (an int 0-100)

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS locations (
  id INTEGER PRIMARY KEY,
  city TEXT NOT NULL,      -- json {{"en", "fr"}}
  country TEXT NOT NULL    -- json {{"en", "fr"}}
);
CREATE TABLE IF NOT EXISTS bloc_contact (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  website TEXT NOT NULL,
  github TEXT,
  linkedin TEXT,
  location_id INTEGER REFERENCES locations(id)
);
CREATE TABLE IF NOT EXISTS bloc_profile (
  id INTEGER PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  text TEXT NOT NULL       -- json
);
CREATE TABLE IF NOT EXISTS bloc_languages (
  id INTEGER PRIMARY KEY,
  sort_order INTEGER NOT NULL,
  name TEXT NOT NULL,      -- json
  level TEXT NOT NULL      -- json
);
CREATE TABLE IF NOT EXISTS bloc_skill_layout (
  row INTEGER NOT NULL,
  position INTEGER NOT NULL,
  label TEXT NOT NULL,     -- json
  PRIMARY KEY (row, position)
);
CREATE TABLE IF NOT EXISTS bloc_education (
  id INTEGER PRIMARY KEY,
  degree TEXT NOT NULL,       -- json
  institution TEXT NOT NULL,  -- json
  start_at TEXT NOT NULL,
  end_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bloc_projects (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  tech TEXT NOT NULL,      -- json
  link TEXT NOT NULL,
  duration TEXT NOT NULL   -- json
);
CREATE TABLE IF NOT EXISTS bloc_certifications (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  issuer TEXT NOT NULL,
  link TEXT NOT NULL,
  date TEXT
);
CREATE TABLE IF NOT EXISTS companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL       -- json; employers, self-employment and offer companies alike
);
CREATE TABLE IF NOT EXISTS contracts (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  type TEXT NOT NULL CHECK (type IN ('job', 'freelance')),
  start_at TEXT NOT NULL,
  end_at TEXT
);
CREATE TABLE IF NOT EXISTS bloc_experiences (
  id INTEGER PRIMARY KEY,
  contract_id INTEGER NOT NULL REFERENCES contracts(id),
  role TEXT NOT NULL,      -- json
  location TEXT            -- json ("Morocco" / "Maroc"); free text, not linked to locations (countries and cities)
);
CREATE TABLE IF NOT EXISTS bloc_activities (
  id INTEGER PRIMARY KEY,
  experience_id INTEGER NOT NULL REFERENCES bloc_experiences(id),
  label TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);
CREATE TABLE IF NOT EXISTS bloc_descriptions (
  id INTEGER PRIMARY KEY,
  activity_id INTEGER NOT NULL REFERENCES bloc_activities(id),
  kind TEXT NOT NULL CHECK (kind IN ('description', 'bullet')),
  text TEXT NOT NULL,      -- json
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS skills (
  id INTEGER PRIMARY KEY,
  type TEXT CHECK (type IN ({', '.join(repr(t) for t in SKILL_TYPES)})),  -- NULL = not typed yet
  name TEXT NOT NULL,      -- json, lowercase
  start_at TEXT,
  end_at TEXT,
  confirmed INTEGER NOT NULL DEFAULT 1 CHECK (confirmed IN (0, 1)),  -- 0 = created from a posting, to review or merge
  ignored INTEGER NOT NULL DEFAULT 0 CHECK (ignored IN (0, 1))  -- 1 = left out of every job's requirements and scoring
);
CREATE TABLE IF NOT EXISTS skill_keywords (
  id INTEGER PRIMARY KEY,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,   -- lowercase; a skill's own name is one of its keywords
  lang TEXT NOT NULL CHECK (lang IN ('en', 'fr')),
  UNIQUE (keyword, lang)
);
CREATE TABLE IF NOT EXISTS description_skills (
  description_id INTEGER NOT NULL REFERENCES bloc_descriptions(id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (description_id, skill_id)
);
CREATE TABLE IF NOT EXISTS cover_paragraphs (
  id INTEGER PRIMARY KEY,
  part TEXT NOT NULL CHECK (part IN ('opening', 'example', 'support', 'close')),
  text TEXT NOT NULL,      -- json
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS cover_paragraph_experiences (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id) ON DELETE CASCADE,
  experience_id INTEGER NOT NULL REFERENCES bloc_experiences(id) ON DELETE CASCADE,
  PRIMARY KEY (paragraph_id, experience_id)
);
CREATE TABLE IF NOT EXISTS cover_paragraph_skills (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (paragraph_id, skill_id)
);
CREATE TABLE IF NOT EXISTS offers (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  title TEXT NOT NULL,
  link TEXT,
  posting TEXT NOT NULL,
  language TEXT NOT NULL,
  english_mentioned INTEGER NOT NULL DEFAULT 0 CHECK (english_mentioned IN (0, 1)),
  location_id INTEGER REFERENCES locations(id),
  created_at TEXT NOT NULL DEFAULT (date('now')),
  resume_url TEXT,         -- one public link per offer; the cover letter is inside the same PDF
  skipped_terms TEXT       -- json {{term: reason}}; open point: a table or nothing
);
CREATE TABLE IF NOT EXISTS compositions (
  id INTEGER PRIMARY KEY,
  offer_id INTEGER REFERENCES offers(id),   -- optional: a resume can be composed without an offer
  folder TEXT NOT NULL UNIQUE,              -- jobs/<slug>-vN: where its files are
  pdf_name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  sent_at TEXT,
  template_sha TEXT
);
CREATE TABLE IF NOT EXISTS offer_lines (
  composition_id INTEGER NOT NULL REFERENCES compositions(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  description_id INTEGER NOT NULL REFERENCES bloc_descriptions(id),
  PRIMARY KEY (composition_id, position)
);
CREATE TABLE IF NOT EXISTS requirements (
  id INTEGER PRIMARY KEY,
  offer_id INTEGER NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
  keyword_id INTEGER NOT NULL REFERENCES skill_keywords(id),
  priority INTEGER NOT NULL CHECK (priority BETWEEN 0 AND 100),
  min_years REAL CHECK (min_years IS NULL OR min_years > 0),
  UNIQUE (offer_id, keyword_id)
);
CREATE TABLE IF NOT EXISTS interview_notes (
  requirement_id INTEGER PRIMARY KEY REFERENCES requirements(id) ON DELETE CASCADE,
  note TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
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
    return con


def i18n(en: str | None, fr: str | None = None) -> str:
    """The JSON stored for a multilingual text; a French equal to the English is not repeated."""
    value = {"en": en or ""}
    if fr and fr != en:
        value["fr"] = fr
    return json.dumps(value, ensure_ascii=False)


def tr(value: str | None, lang: str = "en") -> str:
    """A multilingual JSON column in one language; English when that language is missing."""
    if not value:
        return ""
    data = json.loads(value)
    return data.get(lang) or data.get("en", "")


def has(value: str | None, lang: str) -> bool:
    """Whether a multilingual JSON column holds that language (a missing translation is a warning, not an error)."""
    return bool(value) and bool(json.loads(value).get(lang))


EN = "json_extract({}, '$.en')"  # SQL: a JSON column's English text, e.g. EN.format("d.text")


def clean(word: str) -> str:
    """How a keyword is stored: lowercase, one space between words, plain hyphens."""
    return re.sub(r"\s+", " ", re.sub(r"[‐-―]", "-", word)).strip().lower()


def spelling(word: str) -> str:
    """The comparison form of a keyword: spaces, hyphens and dots don't count ('event-driven' = 'event driven',
    'node.js' = 'nodejs'). Plurals are handled in find_keyword."""
    return re.sub(r"[\s.\-]+", "", clean(word))


def find_keyword(con: sqlite3.Connection, word: str, lang: str = "en") -> int | None:
    """An existing keyword spelled the same way: same comparison form, or the same word with or without a final s
    ('apis' finds 'api' and the other way round). Same language first, then English."""
    key = spelling(word)
    forms = {key} | ({key[:-1]} if key.endswith("s") and len(key) > 3 else set()) | {key + "s"}
    rows = con.execute("SELECT id, keyword, lang FROM skill_keywords ORDER BY lang = ? DESC, lang = 'en' DESC, id",
                       (lang,)).fetchall()
    return next((r[0] for r in rows if spelling(r[1]) == key), None) or \
        next((r[0] for r in rows if spelling(r[1]) in forms), None)


def keyword_id(con: sqlite3.Connection, word: str, lang: str = "en", kind: str | None = None,
               confirmed: bool = False) -> int:
    """The keyword for a word: an existing one spelled the same way (find_keyword), or a new skill (type `kind`,
    not typed yet when None; confirmed = 0 unless it comes from your own resume) whose name is its first keyword.
    A known keyword keeps its skill; the skill's type is only filled in when it had none."""
    if found := find_keyword(con, word, lang):
        if kind:
            con.execute("UPDATE skills SET type = ? WHERE type IS NULL AND id = (SELECT skill_id FROM skill_keywords "
                        "WHERE id = ?)", (kind, found))
        return found
    word = clean(word)
    sid = con.execute("INSERT INTO skills (type, name, confirmed) VALUES (?, ?, ?)",
                      (kind, i18n(word), int(confirmed))).lastrowid
    return con.execute("INSERT INTO skill_keywords (skill_id, keyword, lang) VALUES (?, ?, ?)", (sid, word, lang)).lastrowid


def aliases(con: sqlite3.Connection | None = None) -> dict[str, list[str]]:
    """Posting word -> the English words a resume may use for the same skill (its English keywords).
    One skill with its keywords is one set of true synonyms; a skill's name is one of its keywords."""
    con = con or connect()
    out: dict[str, list[str]] = {}
    for (sid,) in con.execute("SELECT id FROM skills"):
        rows = con.execute("SELECT keyword, lang FROM skill_keywords WHERE skill_id = ?", (sid,)).fetchall()
        english = [k for k, lang in rows if lang == "en"]
        for word, _ in rows:
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


assert tr(i18n("Native", "Natif"), "fr") == "Natif" and tr(i18n("Native"), "fr") == "Native"
assert json.loads(i18n("Java", "Java")) == {"en": "Java"}
assert spelling("Event-Driven") == spelling("event driven") and spelling("Node.js") == spelling("nodejs")
assert clean("  CI/CD   Pipelines ") == "ci/cd pipelines"

if __name__ == "__main__":
    if sys.argv[1:] == ["dump"]:
        print(f"Wrote {dump()}")
    elif sys.argv[1:] == ["restore"]:
        print(f"Rebuilt {restore()} from {DUMP.name}")
    elif sys.argv[1:] == ["reset"]:
        import master  # late: master imports this module
        connect(empty=True).close()
        master.import_files()
    else:
        sys.exit(__doc__)
