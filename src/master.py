#!/usr/bin/env python3
"""The master resume lives in data/resume.db; template/content/default.json and default-fr.json are generated.

Usage:
  python3 src/master.py write     # regenerate both files from the db (refuses if one was edited by hand)
  python3 src/master.py check     # exit 1 if a file differs from what the db generates
  python3 src/master.py set summary|role "<English>" ["<French>"]
  python3 src/master.py set skill <row> <position> "<English label>" ["<French label>"]
  python3 src/master.py set line <activity id> "<English>" ["<French>"]   # becomes that activity's master line
  python3 src/master.py set contact <email|phone|phone_link|location_en|location_fr|website|website_link|github|linkedin> "<value>"
  python3 src/master.py import    # one-time: load both files into the db (contact, skills layout, languages,
                                  # experience display, master line per activity, projects), then verify

Edit the master through the db (src/master.py helpers or SQL), never the generated files: the next write
would refuse (and tell you) rather than lose the edit.
"""

import hashlib
import json
import sys
from pathlib import Path

import db
import db_sync

ROOT = db.ROOT
FILES = {"en": ROOT / "template" / "content" / "default.json", "fr": ROOT / "template" / "content" / "default-fr.json"}
STAMP = ROOT / "template" / "content" / ".generated.json"  # sha256 of what was last written, to spot hand edits


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_FR = ["Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc."]


def label(value: str | None, lang: str) -> str:
    """'2026-09' -> 'Sep 2026' / 'Sept. 2026'; '2016' -> '2016'; None -> 'Present' / 'Présent'."""
    if not value:
        return "Présent" if lang == "fr" else "Present"
    year, _, month = value.partition("-")
    if not month:
        return year
    return f"{(MONTHS_FR if lang == 'fr' else MONTHS_EN)[int(month) - 1]} {year}"


def generate(lang: str = "en", con=None) -> dict:
    con = con or db.connect()
    fr = lang == "fr"
    pick = lambda en, fr_: (fr_ if fr and fr_ else en)
    c = con.execute("SELECT * FROM contact WHERE id = 1").fetchone()
    profile = {k: (pick(en, f)) for k, en, f in con.execute("SELECT key, text_en, text_fr FROM profile")}
    out = {"lang": "fr"} if fr else {}
    out.update({
        "name": c["name"], "role": profile["role"],
        "contact": {"phone": c["phone"], "phone_link": c["phone_link"], "email": c["email"],
                    "location": pick(c["location_en"], c["location_fr"]), "website": c["website"],
                    "website_link": c["website_link"], "github": c["github"], "linkedin": c["linkedin"]},
        "summary": profile["summary"], "skills": [], "experience": []})
    for (row,) in con.execute("SELECT DISTINCT row FROM skill_layout ORDER BY row"):
        out["skills"].append([pick(en, f) for en, f in con.execute(
            "SELECT label_en, label_fr FROM skill_layout WHERE row = ? ORDER BY position", (row,))])
    for e in con.execute("SELECT e.*, c.name AS company FROM experiences e JOIN companies c ON c.id = e.company_id "
                         "WHERE e.sort_order < 100 ORDER BY e.sort_order").fetchall():
        detail = pick(e["detail"] or "", e["detail_fr"])
        company = pick(e["company"], e["company_fr"])
        description, bullets = "", []
        for d in con.execute("SELECT d.kind, d.text_en, d.text_fr FROM activities a JOIN descriptions d ON d.id = a.master_id "
                             "WHERE a.experience_id = ? AND a.active = 1 ORDER BY a.sort_order", (e["id"],)):
            text = pick(d["text_en"], d["text_fr"])
            if d["kind"] == "description":
                description = text
            else:
                bullets.append(text)
        out["experience"].append({
            "dates": f"{label(e['start_at'], lang)} - {label(e['end_at'], lang)}",
            "company": company + ("," if detail and not detail.startswith("-") else ""),
            "detail": detail, "role": pick(e["role"], e["role_fr"]), "description": description, "bullets": bullets})
    out["projects"] = [{"dates": pick(p["duration"], p["duration_fr"]), "name": p["name"], "tech": pick(p["tech"], p["tech_fr"]),
                        "link": p["link"]} for p in con.execute("SELECT * FROM projects ORDER BY id")]
    out["education"] = [{"dates": f"{e['start_at']} - {e['end_at']}", "degree": pick(e["degree_en"], e["degree_fr"]),
                         "institution": pick(e["institution_en"], e["institution_fr"])}
                        for e in con.execute("SELECT * FROM education ORDER BY id")]
    out["certifications"] = [{"name": x["name"], "issuer": x["issuer"], "link": x["link"]}
                             for x in con.execute("SELECT * FROM certifications ORDER BY id")]
    out["languages"] = [{"language": pick(x["name_en"], x["name_fr"]), "level": pick(x["level_en"], x["level_fr"])}
                        for x in con.execute("SELECT * FROM languages ORDER BY sort_order")]
    return out


def text(content: dict) -> str:
    return json.dumps(content, indent=2, ensure_ascii=False) + "\n"


def hand_edited() -> list[Path]:
    """Generated files changed since the last write (someone edited them instead of the db)."""
    stamp = json.loads(STAMP.read_text(encoding="utf-8")) if STAMP.exists() else {}
    return [p for lang, p in FILES.items() if p.exists() and stamp.get(lang) not in (None, sha(p.read_text(encoding="utf-8")))]


def write(con=None) -> list[Path]:
    if edited := hand_edited():
        raise SystemExit(f"{', '.join(p.name for p in edited)} changed by hand since it was generated. The master resume "
                         "lives in data/resume.db: move the change there, then rerun (the file was left as it is).")
    con = con or db.connect()
    written = {}
    for lang, path in FILES.items():
        written[lang] = text(generate(lang, con))
        path.write_text(written[lang], encoding="utf-8")
    STAMP.write_text(json.dumps({lang: sha(t) for lang, t in written.items()}, indent=2) + "\n", encoding="utf-8")
    return list(FILES.values())


def set_value(args: list[str], con=None) -> None:
    """Change the master in the db, then regenerate the files."""
    con = con or db.connect()
    what = args[0]
    if what in ("summary", "role"):
        con.execute("UPDATE profile SET text_en = ?, text_fr = coalesce(?, text_fr) WHERE key = ?",
                    (args[1], args[2] if len(args) > 2 else None, what))
    elif what == "skill":
        row, position = int(args[1]), int(args[2])
        con.execute("INSERT INTO skill_layout VALUES (?, ?, ?, ?) ON CONFLICT (row, position) DO UPDATE SET "
                    "label_en = excluded.label_en, label_fr = excluded.label_fr",
                    (row, position, args[3], args[4] if len(args) > 4 else None))
    elif what == "line":
        activity = con.execute("SELECT experience_id, master_id FROM activities WHERE id = ?", (int(args[1]),)).fetchone()
        kind = con.execute("SELECT kind FROM descriptions WHERE id = ?", (activity["master_id"],)).fetchone()
        kind = kind["kind"] if kind else "bullet"
        con.execute("INSERT OR IGNORE INTO descriptions (experience_id, activity_id, kind, text_en, text_fr) VALUES (?, ?, ?, ?, ?)",
                    (activity["experience_id"], int(args[1]), kind, args[2], args[3] if len(args) > 3 else None))
        line = con.execute("SELECT id FROM descriptions WHERE experience_id = ? AND text_en = ?",
                           (activity["experience_id"], args[2])).fetchone()
        db_sync.link_skills(con, "description_skills", "description_id", line["id"], args[2])
        con.execute("UPDATE activities SET master_id = ? WHERE id = ?", (line["id"], int(args[1])))
    elif what == "contact" and args[1] in {"email", "phone", "phone_link", "location_en", "location_fr", "website",
                                           "website_link", "github", "linkedin"}:
        con.execute(f"UPDATE contact SET {args[1]} = ? WHERE id = 1", (args[2],))
    else:
        raise SystemExit(__doc__)
    con.commit()
    db.dump(con)
    write(con)
    print(f"Master updated ({what}); default.json and default-fr.json regenerated.")


def import_files() -> None:
    """One-time: the current default.json / default-fr.json into the db, then prove the db regenerates them exactly."""
    con = db.connect()
    en, fr = (json.loads(p.read_text(encoding="utf-8")) for p in FILES.values())
    c = en["contact"]
    con.execute("DELETE FROM contact")
    con.execute("INSERT INTO contact (id, name, email, phone, phone_link, location_en, location_fr, website, website_link, "
                "github, linkedin) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (en["name"], c["email"], c["phone"], c["phone_link"], c["location"], fr["contact"]["location"],
                 c["website"], c["website_link"], c.get("github"), c.get("linkedin")))
    for key in ("summary", "role"):
        con.execute("UPDATE profile SET text_en = ?, text_fr = ? WHERE key = ?", (en[key], fr[key], key))
    con.execute("DELETE FROM skill_layout")
    for r, (row, row_fr) in enumerate(zip(en["skills"], fr["skills"]), 1):
        for i, (label_en, label_fr) in enumerate(zip(row, row_fr), 1):
            con.execute("INSERT INTO skill_layout VALUES (?, ?, ?, ?)", (r, i, label_en, label_fr if label_fr != label_en else None))
    con.execute("DELETE FROM languages")
    for i, (x, xf) in enumerate(zip(en["languages"], fr["languages"]), 1):
        con.execute("INSERT INTO languages (sort_order, name_en, name_fr, level_en, level_fr) VALUES (?, ?, ?, ?, ?)",
                    (i, x["language"], xf["language"], x["level"], xf["level"]))
    ids = {n: x for x, n in con.execute("SELECT e.id, c.name FROM experiences e JOIN companies c ON c.id = e.company_id")}
    con.execute("UPDATE experiences SET sort_order = sort_order + 100")  # experiences not in the master stay hidden
    con.execute("UPDATE activities SET master_id = NULL")
    for order, (e, ef) in enumerate(zip(en["experience"], fr["experience"])):
        x = ids[db_sync.company_name(e)]
        company_fr = ef["company"].strip().rstrip(",").strip()
        con.execute("UPDATE experiences SET sort_order = ?, role = ?, role_fr = ?, detail = ?, detail_fr = ?, company_fr = ? "
                    "WHERE id = ?", (order, e["role"], ef["role"] if ef["role"] != e["role"] else None, e["detail"] or None,
                                     ef["detail"] if ef["detail"] != e["detail"] else None,
                                     company_fr if company_fr != db_sync.company_name(e) else None, x))
        lines = ([("description", e["description"], ef["description"])] if e["description"] else []) + \
                [("bullet", b, bf) for b, bf in zip(e["bullets"], ef["bullets"])]
        for slot, (kind, text_en, text_fr) in enumerate(lines, 1):
            d = con.execute("SELECT id, activity_id FROM descriptions WHERE experience_id = ? AND text_en = ?",
                            (x, text_en)).fetchone()
            if d is None:
                raise SystemExit(f"master line not in the library: {text_en[:70]}")
            con.execute("UPDATE descriptions SET text_fr = ? WHERE id = ?", (text_fr, d["id"]))
            con.execute("UPDATE activities SET master_id = ?, sort_order = ?, active = 1 WHERE id = ?",
                        (d["id"], slot, d["activity_id"]))
    for p, pf in zip(en["projects"], fr["projects"]):
        con.execute("UPDATE projects SET tech_fr = ?, duration_fr = ? WHERE name = ?",
                    (pf["tech"] if pf["tech"] != p["tech"] else None, pf["dates"], p["name"]))
    for lang, path in FILES.items():
        if generate(lang, con) != json.loads(path.read_text(encoding="utf-8")):
            got, want = generate(lang, con), json.loads(path.read_text(encoding="utf-8"))
            diff = [k for k in want if got.get(k) != want[k]]
            con.rollback()
            raise SystemExit(f"{path.name}: the db doesn't regenerate it exactly (differs in {diff}); nothing saved.")
    con.commit()
    db.dump(con)
    STAMP.write_text(json.dumps({lang: sha(path.read_text(encoding="utf-8")) for lang, path in FILES.items()},
                                indent=2) + "\n", encoding="utf-8")
    print("Imported; the db regenerates default.json and default-fr.json exactly.")


assert label("2026-09", "en") == "Sep 2026" and label("2026-09", "fr") == "Sept. 2026" and label(None, "fr") == "Présent"

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
