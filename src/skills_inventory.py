#!/usr/bin/env python3
"""Years of experience per skill, for application forms. Data: template/skills.json.

Usage:
  python3 src/skills_inventory.py sync                  # add every skill found on any resume (start unknown)
  python3 src/skills_inventory.py missing               # skills that still need a start date
  python3 src/skills_inventory.py set "Vue 3" 2026-10   # record a start date (YYYY or YYYY-MM); optional end date
  python3 src/skills_inventory.py job jobs/<slug>       # the job's skills with years, as on its dashboard

Each entry: {"name", "match": [other words for it in postings], "start": "YYYY-MM" | null, "end": null}.
A resume skill item like "React / Next.js" or "Accessibility (WCAG)" counts as several skills.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "template" / "skills.json"


def atoms(item: str) -> list[tuple[str, list[str]]]:
    """'React / Next.js' -> [('React', []), ('Next.js', [])]; 'Accessibility (WCAG)' -> [('Accessibility', ['WCAG'])].
    ' / ' with spaces splits; 'CI/CD' stays one skill."""
    out = []
    for part in re.split(r"\s+/\s+|\s+&\s+", item):
        inner = re.findall(r"\(([^)]+)\)", part)
        name = re.sub(r"\s*\([^)]*\)", "", part).strip()
        if name:
            out.append((name, [i.strip() for i in inner if i.strip()]))
    return out


def load() -> dict:
    return json.loads(INVENTORY.read_text(encoding="utf-8")) if INVENTORY.exists() else {"skills": []}


def save(inv: dict) -> None:
    inv["skills"].sort(key=lambda s: s["name"].casefold())
    INVENTORY.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def months(value: str, end_of_period: bool = False) -> int:
    year, _, month = value.partition("-")
    return int(year) * 12 + (int(month) if month else (12 if end_of_period else 1))


def years(skill: dict, today: date | None = None) -> float | None:
    """Start to end (or today), in years, rounded to the nearest half year; None without a start date."""
    if not skill.get("start"):
        return None
    today = today or date.today()
    end = months(skill["end"], end_of_period=True) if skill.get("end") else today.year * 12 + today.month
    return max(0.5, round((end - months(skill["start"]) + 1) / 6) / 2)


def label(n: float | None) -> str:
    if n is None:
        return "start date needed"
    return f"{n:g} year" + ("" if n <= 1 else "s")


def find(inv: dict, word: str) -> dict | None:
    w = word.casefold()
    return next((s for s in inv["skills"] if w == s["name"].casefold() or w in (m.casefold() for m in s["match"])), None)


def resume_skills(content: dict) -> list[str]:
    return [name for row in content.get("skills", []) for item in row for name, _ in atoms(item)]


def sync(inv: dict) -> list[str]:
    added = []
    for path in [ROOT / "template" / "default.json", *sorted((ROOT / "jobs").glob("*/content.json"))]:
        for row in json.loads(path.read_text(encoding="utf-8")).get("skills", []):
            for item in row:
                for name, aliases in atoms(item):
                    if found := find(inv, name):
                        found["match"] += [a for a in aliases if not find(inv, a)]
                    else:
                        inv["skills"].append({"name": name, "match": aliases, "start": None, "end": None})
                        added.append(name)
    return added


def job_skills(job: dict, content: dict, inv: dict | None = None) -> list[dict]:
    """The resume's skills with years, flagged when the posting asks for them (a requirement term matches)."""
    inv = inv or load()
    asked = {t.casefold() for r in job.get("requirements", []) for t in r.get("terms", [])}
    out, seen = [], set()
    for name in resume_skills(content):
        skill = find(inv, name) or {"name": name, "match": [], "start": None}
        if skill["name"] in seen:
            continue
        seen.add(skill["name"])
        words = {skill["name"].casefold(), *(m.casefold() for m in skill["match"])}
        out.append({"name": skill["name"], "years": years(skill), "in_job": bool(words & asked)})
    return sorted(out, key=lambda s: (not s["in_job"], s["name"].casefold()))


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in {"sync", "missing", "set", "job"}:
        sys.exit(__doc__)
    inv = load()
    if sys.argv[1] == "sync":
        added = sync(inv)
        save(inv)
        print(f"Added {len(added)} skill(s): {', '.join(added) or 'none'}")
    elif sys.argv[1] == "missing":
        todo = [s["name"] for s in inv["skills"] if not s.get("start")]
        print("\n".join(f"{n}: YYYY-MM" for n in todo) or "Every skill has a start date.")
    elif sys.argv[1] == "set":
        skill = find(inv, sys.argv[2]) or sys.exit(f"Unknown skill '{sys.argv[2]}'; run sync first.")
        skill["start"] = sys.argv[3]
        skill["end"] = sys.argv[4] if len(sys.argv) > 4 else None
        months(skill["start"])  # validates the format
        save(inv)
        print(f"{skill['name']}: {label(years(skill))}")
    else:
        folder = Path(sys.argv[2])
        rows = job_skills(json.loads((folder / "job.json").read_text(encoding="utf-8")),
                          json.loads((folder / "content.json").read_text(encoding="utf-8")), inv)
        for s in rows:
            print(f"{'*' if s['in_job'] else ' '} {s['name']}: {label(s['years'])}")


assert atoms("React / Next.js") == [("React", []), ("Next.js", [])]
assert atoms("Git / CI/CD") == [("Git", []), ("CI/CD", [])]
assert atoms("Accessibility (WCAG)") == [("Accessibility", ["WCAG"])]
assert years({"start": "2024-01"}, date(2026, 6, 1)) == 2.5
assert years({"start": "2016", "end": "2020"}, date(2026, 6, 1)) == 5
assert years({"start": None}) is None

if __name__ == "__main__":
    main()
