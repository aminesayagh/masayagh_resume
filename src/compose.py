#!/usr/bin/env python3
"""Compose a job's experience lines from the library: one line per active activity, chosen for this offer.

Usage: python3 src/compose.py jobs/<slug>       (after the requirements are drafted; then run src/tailor.py)

For each experience (master order) and each of its active activities, the best candidate is chosen by
src/pick.py: only candidates with every language the job needs (English, plus French for a local French version),
reviewed ones first, ranked by 0.5 × Haiku quality + 0.5 × the offer's requirement terms they contain (weighted by
skill type and priority, a skill's keywords counting as the term); on a tie, the most recently added line wins. Only experience descriptions and bullets change: summary, title and skills stay as they are.
Writes jobs/<slug>/content/content.json (text only) and records in the db which library lines the composition uses
(offer_lines, so a line approved later joins the right activity); prints the choice per activity.
"""

import json
import sys
from pathlib import Path

import build_resume
import db
import db_sync
import paths
import offers
import pick


def compose(folder: Path) -> dict:
    folder = folder.resolve()
    if reason := build_resume.frozen(folder):
        raise SystemExit(reason)
    job = offers.load(folder)
    if not job.get("requirements"):
        raise SystemExit("No requirements yet: draft them first, then compose.")
    content = json.loads(paths.content(folder).read_text(encoding="utf-8"))
    con = db.connect()
    comp = offers.composition(folder, con)["id"]
    if con.execute("SELECT 1 FROM offer_lines WHERE composition_id = ?", (comp,)).fetchone():  # first composition only
        raise SystemExit("This job is already composed; its lines may hold edits approved for it. Change only the "
                         "lines we agree on (the next build records them in their activity).")
    terms = pick.job_terms(job, db.aliases(con))
    langs = ("en", "fr") if job.get("french_version") else ("en",)
    report, used = [], []
    experiences = db_sync.experience_ids(con)
    for entry in content["experience"]:
        name = db_sync.company_name(entry)
        exp = experiences.get(name.casefold())
        if exp is None:
            report.append(f"{name}: not in the library, left as it is")
            continue
        chosen = []  # library line ids, in resume order (description first)
        description, bullets = "", []
        for aid, label in con.execute("SELECT id, label FROM bloc_activities WHERE experience_id = ? AND active = 1 "
                                      "ORDER BY sort_order", (exp,)).fetchall():
            lines = pick.candidates(con, aid)
            best, hits, warn = pick.best(lines, langs, terms)
            if best is None:
                report.append(f"{name} · {label}: {warn}")
                continue
            if best["kind"] == "description":
                description = best["text_en"]
                chosen.insert(0, best["id"])
            else:
                bullets.append(best["text_en"])
                chosen.append(best["id"])
            report.append(f"{name} · {label}: line {best['id']} of {len(lines)}"
                          + (f" — terms: {', '.join(hits)}" if hits else " — no offer terms (quality decides)")
                          + (f" — WARNING: {warn}" if warn else ""))
        entry["description"], entry["bullets"] = description, bullets
        used += chosen
    con.executemany("INSERT INTO offer_lines VALUES (?, ?, ?)",  # what this composition uses, kept in the db only
                    [(comp, i, line) for i, line in enumerate(used)])
    paths.content(folder).write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    con.commit()
    db.dump(con)
    print("\n".join(report))
    return content



if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    compose(Path(sys.argv[1]))
