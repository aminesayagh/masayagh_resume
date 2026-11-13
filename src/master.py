#!/usr/bin/env python3
"""The master resume lives in data/resume.db; template/content/default.json and default-fr.json are generated.

Usage:
  python3 src/master.py write     # regenerate both files from the db (refuses if one was edited by hand)
  python3 src/master.py check     # exit 1 if a file differs from what the db generates
  python3 src/master.py set summary|role "<English>" ["<French>"]   # a new version: the best-reviewed one is shown
  python3 src/master.py set skill <row> <position> "<English label>" ["<French label>"]
  python3 src/master.py set line <activity id> "<English>" ["<French>"]   # a new candidate: the best-reviewed one is shown (src/pick.py)
  python3 src/master.py set new-line <experience id> "<English>" ["<French>"]   # a new activity with its first line
  python3 src/master.py set contact <email|phone|website|github|linkedin> "<value>"
  python3 src/master.py import    # load both files into an empty db (python3 src/db.py reset does it)

Each active activity shows its best-reviewed candidate with English and French text (src/pick.py; no master pick is stored); experiences are ordered by their
contract dates, newest first. phone_link and website_link are derived from phone and website.
Edit the master through the db (src/master.py helpers or SQL), never the generated files: the next write
would refuse (and tell you) rather than lose the edit.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

import db
from db import i18n, tr

ROOT = db.ROOT
FILES = {"en": ROOT / "template" / "content" / "default.json", "fr": ROOT / "template" / "content" / "default-fr.json"}
STAMP = ROOT / "template" / "content" / ".generated.json"  # sha256 of what was last written, to spot hand edits
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_FR = ["Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc."]


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def label(value: str | None, lang: str) -> str:
    """'2026-09' -> 'Sep 2026' / 'Sept. 2026'; '2016' -> '2016'; None -> 'Present' / 'Présent'."""
    if not value:
        return "Présent" if lang == "fr" else "Present"
    year, _, month = value.partition("-")
    if not month:
        return year
    return f"{(MONTHS_FR if lang == 'fr' else MONTHS_EN)[int(month) - 1]} {year}"


def unlabel(text: str) -> str | None:
    """The inverse of label() for English dates: 'Sep 2026' -> '2026-09', '2016' -> '2016', 'Present' -> None."""
    if text == "Present":
        return None
    month, _, year = text.rpartition(" ")
    return f"{year}-{MONTHS_EN.index(month) + 1:02d}" if month else year


def phone_link(phone: str) -> str:
    return "tel:+" + re.sub(r"\D", "", phone)


def website_link(website: str) -> str:
    return website if website.startswith("http") else f"https://www.{website.removeprefix('www.')}"


def place(con, location_id: int | None, lang: str) -> str:
    row = con.execute("SELECT city, country FROM locations WHERE id = ?", (location_id,)).fetchone()
    return f"{tr(row['city'], lang)}, {tr(row['country'], lang)}" if row else ""


def location_id(con, text: str | None, text_fr: str | None = None) -> int | None:
    """'Casablanca, Morocco' (+ French) -> a locations row, reused when the same city and country exist."""
    if not text or "," not in text:
        return None
    city, _, country = (p.strip() for p in text.rpartition(","))
    city_fr, _, country_fr = (p.strip() for p in (text_fr or text).rpartition(","))
    row = con.execute(f"SELECT id FROM locations WHERE lower({db.EN.format('city')}) = lower(?) "
                      f"AND lower({db.EN.format('country')}) = lower(?)", (city, country)).fetchone()
    return row[0] if row else con.execute("INSERT INTO locations (city, country) VALUES (?, ?)",
                                         (i18n(city, city_fr), i18n(country, country_fr))).lastrowid


def experiences(con) -> list:
    """Experiences with their company and contract, newest contract first."""
    return con.execute("SELECT e.id, e.role, e.location, c.name AS company, k.start_at, k.end_at FROM bloc_experiences e "
                       "JOIN contracts k ON k.id = e.contract_id JOIN companies c ON c.id = k.company_id "
                       "ORDER BY k.start_at DESC, e.id").fetchall()


def master_lines(con, experience_id: int) -> list:
    """The line each active activity shows on the master: its best-reviewed candidate with English and French text
    (src/pick.py; no job, so quality alone decides)."""
    import pick  # late: pick imports db only, but keeps master's import list short
    out = []
    for aid, label_ in con.execute("SELECT id, label FROM bloc_activities WHERE experience_id = ? AND active = 1 "
                                   "ORDER BY sort_order", (experience_id,)).fetchall():
        line, _, warn = pick.best(pick.candidates(con, aid), ("en", "fr"))
        if warn:
            print(f"master: {label_}: {warn}", file=sys.stderr)
        if line:
            out.append(line)
    return out


def generate(lang: str = "en", con=None) -> dict:
    con = con or db.connect()
    c = con.execute("SELECT * FROM bloc_contact WHERE id = 1").fetchone()
    import pick  # late, like master_lines
    profile = {k: pick.profile_text(con, k, lang) for (k,) in con.execute("SELECT DISTINCT key FROM bloc_profile")}
    out = {"lang": "fr"} if lang == "fr" else {}
    out.update({
        "name": c["name"], "role": profile.get("role", ""),
        "contact": {"phone": c["phone"], "phone_link": phone_link(c["phone"]), "email": c["email"],
                    "location": place(con, c["location_id"], lang), "website": c["website"],
                    "website_link": website_link(c["website"]), "github": c["github"], "linkedin": c["linkedin"]},
        "summary": profile.get("summary", ""), "skills": [], "experience": []})
    for (row,) in con.execute("SELECT DISTINCT row FROM bloc_skill_layout ORDER BY row"):
        out["skills"].append([tr(t, lang) for (t,) in con.execute(
            "SELECT label FROM bloc_skill_layout WHERE row = ? ORDER BY position", (row,))])
    for e in experiences(con):
        detail = tr(e["location"], lang)
        description, bullets = "", []
        for line in master_lines(con, e["id"]):
            if line["kind"] == "description":
                description = tr(line["text"], lang)
            else:
                bullets.append(tr(line["text"], lang))
        out["experience"].append({
            "dates": f"{label(e['start_at'], lang)} - {label(e['end_at'], lang)}",
            "company": tr(e["company"], lang) + ("," if detail else ""),
            "detail": detail, "role": tr(e["role"], lang), "description": description, "bullets": bullets})
    out["projects"] = [{"dates": tr(p["duration"], lang), "name": p["name"], "tech": tr(p["tech"], lang), "link": p["link"]}
                       for p in con.execute("SELECT * FROM bloc_projects ORDER BY id")]
    out["education"] = [{"dates": f"{e['start_at']} - {e['end_at']}", "degree": tr(e["degree"], lang),
                         "institution": tr(e["institution"], lang)} for e in con.execute("SELECT * FROM bloc_education ORDER BY id")]
    out["certifications"] = [{"name": x["name"], "issuer": x["issuer"], "link": x["link"]}
                             for x in con.execute("SELECT * FROM bloc_certifications ORDER BY id")]
    out["languages"] = [{"language": tr(x["name"], lang), "level": tr(x["level"], lang)}
                        for x in con.execute("SELECT * FROM bloc_languages ORDER BY sort_order")]
    return out


def text(content: dict) -> str:
    return json.dumps(content, indent=2, ensure_ascii=False) + "\n"


def hand_edited() -> list[Path]:
    """Generated files changed since the last write (someone edited them instead of the db)."""
    stamp = json.loads(STAMP.read_text(encoding="utf-8")) if STAMP.exists() else {}
    return [p for lang, p in FILES.items() if p.exists() and stamp.get(lang) not in (None, sha(p.read_text(encoding="utf-8")))]


def write(con=None, force: bool = False) -> list[Path]:
    if not force and (edited := hand_edited()):
        raise SystemExit(f"{', '.join(p.name for p in edited)} changed by hand since it was generated. The master resume "
                         "lives in data/resume.db: move the change there, then rerun (the file was left as it is).")
    con = con or db.connect()
    written = {}
    for lang, path in FILES.items():
        written[lang] = text(generate(lang, con))
        path.write_text(written[lang], encoding="utf-8")
    STAMP.write_text(json.dumps({lang: sha(t) for lang, t in written.items()}, indent=2) + "\n", encoding="utf-8")
    return list(FILES.values())


def add_profile_version(con, key: str, en: str, fr: str | None = None) -> int:
    """A new version of a profile bloc (the old ones are kept; src/pick.py picks the one the resume uses). With no
    French, the newest version's French is reused, as before versions existed."""
    if fr is None:
        last = con.execute("SELECT text FROM bloc_profile WHERE key = ? ORDER BY created_at DESC, id DESC", (key,)).fetchone()
        fr = tr(last[0], "fr") if last and db.has(last[0], "fr") else None
    return con.execute("INSERT INTO bloc_profile (key, text) VALUES (?, ?)", (key, i18n(en, fr))).lastrowid


def set_value(args: list[str], con=None) -> None:
    """Change the master in the db, then regenerate the files."""
    con = con or db.connect()
    what = args[0]
    fr = lambda i: args[i] if len(args) > i else None
    if what in ("summary", "role"):
        add_profile_version(con, what, args[1], fr(2))
    elif what == "skill":
        con.execute("INSERT INTO bloc_skill_layout VALUES (?, ?, ?) ON CONFLICT (row, position) DO UPDATE SET label = excluded.label",
                    (int(args[1]), int(args[2]), i18n(args[3], fr(4))))
    elif what == "line":
        import db_sync  # late: db_sync imports offers, which imports this module's db
        aid = int(args[1])
        kind = con.execute("SELECT kind FROM bloc_descriptions WHERE activity_id = ? LIMIT 1", (aid,)).fetchone()
        db_sync.add_line(con, aid, kind[0] if kind else "bullet", args[2], fr(3))
    elif what == "new-line":  # an experience's next bullet, as a new active activity (e.g. one with no lines yet)
        import db_sync
        xid = int(args[1])
        if not con.execute("SELECT 1 FROM bloc_experiences WHERE id = ?", (xid,)).fetchone():
            raise SystemExit(f"No experience {xid}")
        order = con.execute("SELECT coalesce(max(sort_order), 0) + 1 FROM bloc_activities WHERE experience_id = ?",
                            (xid,)).fetchone()[0]
        aid = con.execute("INSERT INTO bloc_activities (experience_id, label, sort_order, active) VALUES (?, ?, ?, 1)",
                          (xid, " ".join(args[2].split()[:5]), order)).lastrowid
        db_sync.add_line(con, aid, "bullet", args[2], fr(3))
    elif what == "contact" and args[1] in {"email", "phone", "website", "github", "linkedin"}:
        con.execute(f"UPDATE bloc_contact SET {args[1]} = ? WHERE id = 1", (args[2],))
    else:
        raise SystemExit(__doc__)
    con.commit()
    db.dump(con)
    import score_bullet  # late: new lines are scored like every other (one Haiku call each)
    score_bullet.pending(con)
    write(con)
    print(f"Master updated ({what}); default.json and default-fr.json regenerated.")


def import_files(con=None) -> None:
    """Load default.json and default-fr.json into an empty db, then regenerate them and report any difference."""
    con = con or db.connect()
    if con.execute("SELECT 1 FROM bloc_experiences LIMIT 1").fetchone():
        raise SystemExit("The db already holds a master resume; reset it first (python3 src/db.py reset).")
    en, fr = (json.loads(p.read_text(encoding="utf-8")) for p in FILES.values())
    c = en["contact"]
    con.execute("INSERT INTO bloc_contact (id, name, email, phone, website, github, linkedin, location_id) "
                "VALUES (1, ?, ?, ?, ?, ?, ?, ?)", (en["name"], c["email"], c["phone"], c["website"], c.get("github"),
                                                    c.get("linkedin"), location_id(con, c["location"], fr["contact"]["location"])))
    for key in ("role", "summary"):
        add_profile_version(con, key, en[key], fr[key])
    for r, (row, row_fr) in enumerate(zip(en["skills"], fr["skills"]), 1):
        for i, (label_en, label_fr) in enumerate(zip(row, row_fr), 1):
            con.execute("INSERT INTO bloc_skill_layout VALUES (?, ?, ?)", (r, i, i18n(label_en, label_fr)))
            for word in re.split(r"\s+/\s+", label_en):  # a layout item names one or more skills
                db.keyword_id(con, re.sub(r"\s*\([^)]*\)", "", word), confirmed=True)  # your own skills
    for i, (x, xf) in enumerate(zip(en["languages"], fr["languages"]), 1):
        con.execute("INSERT INTO bloc_languages (sort_order, name, level) VALUES (?, ?, ?)",
                    (i, i18n(x["language"], xf["language"]), i18n(x["level"], xf["level"])))
    for e, ef in zip(en["experience"], fr["experience"]):
        name = e["company"].strip().rstrip(",").strip()
        company = con.execute("INSERT INTO companies (name) VALUES (?)",
                              (i18n(name, ef["company"].strip().rstrip(",").strip()),)).lastrowid
        start, _, end = e["dates"].partition(" - ")
        contract = con.execute("INSERT INTO contracts (company_id, type, start_at, end_at) VALUES (?, ?, ?, ?)",
                               (company, "freelance" if name.casefold() == "freelance" else "job",
                                unlabel(start), unlabel(end))).lastrowid
        # ponytail: a detail that isn't a place ("- Hypeo, MENA") has no column since detail was dropped
        location = e["detail"] if e["detail"] and not e["detail"].startswith("-") else None
        x = con.execute("INSERT INTO bloc_experiences (contract_id, role, location) VALUES (?, ?, ?)",
                        (contract, i18n(e["role"], ef["role"]), location and i18n(location, ef["detail"]))).lastrowid
        lines = ([("description", e["description"], ef["description"])] if e["description"] else []) + \
                [("bullet", b, bf) for b, bf in zip(e["bullets"], ef["bullets"])]
        for slot, (kind, text_en, text_fr) in enumerate(lines, 1):
            aid = con.execute("INSERT INTO bloc_activities (experience_id, label, sort_order) VALUES (?, ?, ?)",
                              (x, " ".join(text_en.split()[:5]), slot)).lastrowid
            import db_sync  # late: db_sync imports offers
            db_sync.add_line(con, aid, kind, text_en, text_fr)
    for p, pf in zip(en["projects"], fr["projects"]):
        con.execute("INSERT INTO bloc_projects (name, tech, link, duration) VALUES (?, ?, ?, ?)",
                    (p["name"], i18n(p["tech"], pf["tech"]), p["link"], i18n(p["dates"], pf["dates"])))
    for e, ef in zip(en["education"], fr["education"]):
        start, _, end = e["dates"].partition(" - ")
        con.execute("INSERT INTO bloc_education (degree, institution, start_at, end_at) VALUES (?, ?, ?, ?)",
                    (i18n(e["degree"], ef["degree"]), i18n(e["institution"], ef["institution"]), start, end))
    for x in en["certifications"]:
        con.execute("INSERT INTO bloc_certifications (name, issuer, link) VALUES (?, ?, ?)", (x["name"], x["issuer"], x["link"]))
    con.commit()
    db.dump(con)
    import score_bullet  # late: new lines are scored like every other (one Haiku call each)
    score_bullet.pending(con)
    for lang, path in FILES.items():
        want = json.loads(path.read_text(encoding="utf-8"))
        got = generate(lang, con)
        if got != want:
            print(f"{path.name}: regenerated with differences in {[k for k in want if got.get(k) != want[k]]}")
    write(con, force=True)
    print("Imported default.json and default-fr.json into the db; both files regenerated from it.")


assert label("2026-09", "en") == "Sep 2026" and label("2026-09", "fr") == "Sept. 2026" and label(None, "fr") == "Présent"
assert unlabel("Sep 2026") == "2026-09" and unlabel("2016") == "2016" and unlabel("Present") is None
assert phone_link("(+212) 616-13 71 24") == "tel:+212616137124"
assert website_link("masayagh.com/hire") == "https://www.masayagh.com/hire"

if __name__ == "__main__":
    command = sys.argv[1:] or ["write"]
    if command == ["import"]:
        import_files()
    elif command == ["check"]:
        con = db.connect()
        stale = [p.name for lang, p in FILES.items() if p.read_text(encoding="utf-8") != text(generate(lang, con))]
        print(f"Differs from the db: {', '.join(stale)}" if stale else "Generated files match the db.")
        sys.exit(1 if stale else 0)
    elif command[:1] == ["set"] and len(command) >= 3:
        set_value(command[1:])
    elif command == ["write"]:
        print("Wrote " + ", ".join(p.name for p in write()))
    else:
        sys.exit(__doc__)
