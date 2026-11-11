#!/usr/bin/env python3
"""Build the French version of a job's resume (and cover letter): local only, never published.

Usage: python3 src/build_fr.py jobs/<slug>

Applies when the offer has "french_version": true (a French posting that doesn't ask for English).
1. Translates jobs/<slug>/content/content.json line by line: unchanged template lines reuse template/content/default-fr.json,
   tailored lines reuse template/content/translations-fr.json. Any line still untranslated is written to
   jobs/<slug>/content/translate-fr.json ({"English line": ""}); fill it in, rerun, and the entries move to
   translations-fr.json for every future job.
2. Writes content-fr.json and builds pdf/fr/<stem>-FR.pdf, with the same rules as English: over 3 pages or a broken
   skills layout means a '_' prefix (not ready). While translations are missing, no French PDF is built and
   an existing one is renamed with '_', so a stale French version can't be sent.
3. Builds the French cover letter from cover-fr.json when it exists (build_cover.build(..., lang="fr")).
"""

import json
import re
import shutil
import sys
from pathlib import Path

from pypdf import PdfReader

import build_resume
import paths
import db

ROOT = build_resume.ROOT
TEMPLATE_EN = ROOT / "template" / "content" / "default.json"
TEMPLATE_FR = ROOT / "template" / "content" / "default-fr.json"
MEMORY = ROOT / "template" / "content" / "translations-fr.json"
KEEP = {"lang", "phone", "phone_link", "email", "website", "website_link", "github", "linkedin", "qr_url", "link", "name"}
FRENCH_WORDS = re.compile(r"\b(le|la|les|des|du|et|vous|nous|une|pour|avec|dans|sur)\b", re.I)
ENGLISH_WORDS = re.compile(r"\b(the|and|you|we|with|for|our|your|this|that)\b", re.I)


def is_french_only(posting: str) -> bool:
    """French posting that doesn't ask for English -> a French resume is worth sending."""
    return (len(FRENCH_WORDS.findall(posting)) > 2 * len(ENGLISH_WORDS.findall(posting))
            and not re.search(r"\b(anglais|english)\b", posting, re.I))


def strings(node, key=None):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from strings(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v, key)
    elif isinstance(node, str) and node.strip() and key not in KEEP:
        yield node


def translation_memory() -> dict:
    en, fr = (list(strings(json.loads(p.read_text(encoding="utf-8")))) for p in (TEMPLATE_EN, TEMPLATE_FR))
    if len(en) != len(fr):
        raise ValueError("template/content/default.json and default-fr.json differ in shape; keep them in step")
    memory = dict(zip(en, fr))
    if MEMORY.exists():
        memory.update(json.loads(MEMORY.read_text(encoding="utf-8")))
    con = db.connect()  # French of library lines and skills
    memory.update({en: fr for en, fr in con.execute("SELECT text_en, text_fr FROM descriptions WHERE text_fr IS NOT NULL")})
    memory.update({en: fr for en, fr in con.execute("SELECT name_en, name_fr FROM skills WHERE name_fr IS NOT NULL")})
    return memory


def translate(node, memory: dict, missing: list, key=None):
    if isinstance(node, dict):
        return {k: translate(v, memory, missing, k) for k, v in node.items()}
    if isinstance(node, list):
        return [translate(v, memory, missing, key) for v in node]
    if isinstance(node, str) and node.strip() and key not in KEEP:
        if node not in memory:
            missing.append(node)
        return memory.get(node, node)
    return node


def hide(path: Path) -> None:
    if path.exists():
        shutil.move(str(path), paths.not_ready(path))


def build(folder: Path) -> Path | None:
    folder = folder.resolve()
    if reason := build_resume.frozen(folder):
        raise SystemExit(reason)
    pending = paths.translate_fr(folder)
    if pending.exists():  # merge what was filled in, keep the rest pending
        filled = {k: v for k, v in json.loads(pending.read_text(encoding="utf-8")).items() if v.strip()}
        memory = json.loads(MEMORY.read_text(encoding="utf-8")) if MEMORY.exists() else {}
        con = db.connect()  # library lines and skills keep their French in the db, other strings in translations-fr.json
        rest = {}
        for en_text, fr_text in filled.items():
            hit = con.execute("UPDATE descriptions SET text_fr = ? WHERE text_en = ?", (fr_text, en_text)).rowcount
            hit += con.execute("UPDATE skills SET name_fr = ? WHERE name_en = ?", (fr_text, en_text)).rowcount
            if not hit:
                rest[en_text] = fr_text
        con.commit()
        db.dump(con)
        MEMORY.write_text(json.dumps({**memory, **rest}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        pending.unlink()

    english = json.loads(paths.content(folder).read_text(encoding="utf-8"))
    missing: list[str] = []
    french = translate(english, translation_memory(), missing)
    fr_pdf = paths.resume_pdf(folder, "fr")
    if missing:
        pending.write_text(json.dumps(dict.fromkeys(dict.fromkeys(missing), ""), indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
        hide(fr_pdf)
        print(f"French version NOT built: {len(set(missing))} line(s) to translate in {pending.relative_to(ROOT)}")
        return None

    french["lang"] = "fr"
    fr_content = paths.content(folder, "fr")
    fr_content.write_text(json.dumps(french, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    built = build_resume.build(fr_content, fr_pdf)
    ready = len(PdfReader(built).pages) <= build_resume.MAX_PAGES and not build_resume.skills_problem(french["skills"])
    paths.not_ready(fr_pdf).unlink(missing_ok=True)
    if not ready:
        hide(built)
        print(f"NOT READY TO SEND: French resume saved as _{fr_pdf.name}")
    if paths.cover(folder, "fr").exists():
        import build_cover  # late: imports build_resume
        build_cover.build(folder, lang="fr")
    else:
        print("No cover-fr.json yet: draft the French cover letter (draft-cover-letter skill).")
    return built


assert is_french_only("Nous recherchons un développeur pour la plateforme et les équipes avec vous.")
assert not is_french_only("Nous recherchons un développeur, anglais courant, pour la plateforme et les équipes.")
assert not is_french_only("We are looking for an engineer to join our team and build the platform with you.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]))
