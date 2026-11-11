#!/usr/bin/env python3
"""Compose a job's experience lines from the library: one line per active activity, chosen for this offer.

Usage: python3 src/compose.py jobs/<slug>       (after the requirements are drafted; then run src/tailor.py)

For each experience (master order) and each of its active activities, the line containing the most of the
offer's requirement terms is chosen (a skill's keywords count as the term); on a tie, the most recently added
line wins. Only experience descriptions and bullets change: summary, title and skills stay as they are.
Writes jobs/<slug>/content/content.json and content/composition.json (which activity each line slot belongs to, so a
line approved later joins the right activity) and prints the choice per activity with its alternatives.
"""

import json
import re
import sys
from pathlib import Path

import build_resume
import db
import db_sync
import paths
import offers


def term_patterns(job: dict, aliases: dict[str, list[str]]) -> dict[str, re.Pattern]:
    """Each requirement term -> a pattern for it and its synonyms, as whole words."""
    out = {}
    for r in job.get("requirements", []):
        for t in r.get("terms", []):
            words = [t] + aliases.get(t, []) + next((v for k, v in aliases.items() if k.casefold() == t.casefold()), [])
            out[t] = re.compile("|".join(rf"(?<![\w.]){re.escape(w)}(?![\w])" for w in dict.fromkeys(words)), re.I)
    return out


def matched(text: str, patterns: dict[str, re.Pattern]) -> list[str]:
    return [t for t, p in patterns.items() if p.search(text)]


def choose(lines: list[dict], patterns: dict[str, re.Pattern]) -> tuple[dict, list[str]]:
    """Most offer terms; on a tie the most recent line (created_at, then id)."""
    scored = [(len(m := matched(line["text_en"], patterns)), line.get("created_at", ""), line["id"], line, m) for line in lines]
    *_, best, terms = max(scored, key=lambda s: (s[0], s[1], s[2]))
    return best, terms


def compose(folder: Path) -> dict:
    folder = folder.resolve()
    if reason := build_resume.frozen(folder):
        raise SystemExit(reason)
    job = offers.load(folder)
    if not job.get("requirements"):
        raise SystemExit("No requirements yet: draft them first, then compose.")
    content = json.loads(paths.content(folder).read_text(encoding="utf-8"))
    con = db.connect()
    patterns = term_patterns(job, db.aliases(con))
    composition, report = [], []
    for entry in content["experience"]:
        name = db_sync.company_name(entry)
        exp = con.execute("SELECT e.id FROM experiences e JOIN companies c ON c.id = e.company_id WHERE c.name = ?",
                          (name,)).fetchone()
        if exp is None:
            report.append(f"{name}: not in the library, left as it is")
            continue
        slots = {"company": name, "description": None, "bullets": []}
        description, bullets = "", []
        for aid, label in con.execute("SELECT id, label FROM activities WHERE experience_id = ? AND active = 1 "
                                      "ORDER BY sort_order", (exp[0],)).fetchall():
            lines = [dict(r) for r in con.execute("SELECT id, kind, text_en, created_at FROM descriptions WHERE activity_id = ? "
                                                  "AND status = 'approved'", (aid,))]
            if not lines:
                continue
            best, terms = choose(lines, patterns)
            if best["kind"] == "description":
                description, slots["description"] = best["text_en"], aid
            else:
                bullets.append(best["text_en"])
                slots["bullets"].append(aid)
            report.append(f"{name} · {label}: line {best['id']} of {len(lines)}"
                          + (f" — terms: {', '.join(terms)}" if terms else " — no offer terms (most recent kept)"))
        entry["description"], entry["bullets"] = description, bullets
        composition.append(slots)
    paths.content(folder).write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths.composition(folder).write_text(json.dumps(composition, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(report))
    return content


_P = {"Vue 3": re.compile(r"(?<![\w.])Vue 3(?![\w])", re.I), "APIs": re.compile(r"(?<![\w.])APIs?(?![\w])", re.I)}
assert choose([{"id": 1, "text_en": "Built APIs in Vue 3"}, {"id": 2, "text_en": "Built APIs"}], _P)[0]["id"] == 1
assert choose([{"id": 1, "text_en": "Built APIs"}, {"id": 2, "text_en": "Shipped APIs"}], _P)[0]["id"] == 2  # tie: newest

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    compose(Path(sys.argv[1]))
