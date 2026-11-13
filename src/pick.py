"""Which candidate of a bloc goes on a resume: the best-scored one that has every language the resume needs.

A bloc has candidates: an experience activity's approved lines (bloc_descriptions), or a profile bloc's approved
versions (bloc_profile rows of one key: role, summary, cover greeting/closing), each stored in English and maybe French.
  1. Language: only candidates with text in every needed language (English, plus French when the job gets the local
     French version), so the two versions show the same lines. None has them all -> the English ones, with a warning.
  2. Scored only: a candidate with no Haiku review is left out while a reviewed one exists (none reviewed -> the
     newest, with a warning, so a bloc never disappears while the scorer is down).
  3. score = 0.5 × quality + 0.5 × job match
       quality   = Haiku total / 8 (src/score_bullet.py)
       job match = the job's requirement terms found in the English text, each weighted like evidence coverage
                   (skill type × priority, src/review_ats.py), divided by the best candidate of the bloc: 0-1.
     No job (the master resume) -> job match is 0 for all: the best quality wins. Tie -> the newest.
"""
import json
import re

import db


def eligible(c: dict, langs) -> bool:
    return all(db.has(c["text"], lang) for lang in langs)


def job_terms(job: dict, aliases: dict[str, list[str]]) -> list[tuple[re.Pattern, float, str]]:
    """Each requirement term (and its synonyms) as a whole-word pattern, with its weight: skill type × priority."""
    from review_ats import PRIORITY_WEIGHTS, TYPE_WEIGHTS  # late: review_ats imports a lot
    out = []
    for r in job.get("requirements", []):
        weight = TYPE_WEIGHTS.get(r.get("type"), TYPE_WEIGHTS[None]) * PRIORITY_WEIGHTS.get(r.get("priority"), 0.25)
        for t in r.get("terms", []):
            words = [t] + aliases.get(t, []) + next((v for k, v in aliases.items() if k.casefold() == t.casefold()), [])
            pattern = re.compile("|".join(rf"(?<![\w.]){re.escape(w)}(?![\w])" for w in dict.fromkeys(words)), re.I)
            out.append((pattern, weight, t))
    return out


def matched(text: str, terms) -> tuple[float, list[str]]:
    hits = [(w, t) for p, w, t in terms if p.search(text)]
    return sum(w for w, _ in hits), [t for _, t in hits]


def line_quality(score: dict) -> float:
    return score["total"] / 8  # the bullet rubric (src/score_bullet.py)


def summary_quality(score: dict) -> float:
    """Name / Fame / Aim (src/score_summary.py), 0-2 each; an Aim that isn't needed (null) counts as met."""
    aim = score["aim"]["score"]
    return (score["name"]["score"] + score["fame"]["score"] + (2 if aim is None else aim)) / 6


def best(cands: list[dict], langs=("en",), terms=(), quality=line_quality) -> tuple[dict | None, list[str], str | None]:
    """cands: dicts with id, text (the json column), text_en, score (json or None), created_at.
    Returns (chosen candidate, the job terms it matches, a warning or None)."""
    warn = None
    pool = [c for c in cands if eligible(c, langs)]
    if not pool:
        pool = [c for c in cands if eligible(c, ("en",))]
        warn = f"no candidate in {' + '.join(langs)}; an English-only one is used"
    if not pool:
        return None, [], "no candidate with English text"
    if any(c.get("score") for c in pool):
        pool = [c for c in pool if c.get("score")]
    else:
        warn = (warn + "; " if warn else "") + "no reviewed candidate; the newest is used"
    match = {c["id"]: matched(c["text_en"], terms) for c in pool}
    top = max(w for w, _ in match.values())

    def rank(c):
        q = quality(json.loads(c["score"])) if c.get("score") else 0
        return 0.5 * q + 0.5 * (match[c["id"]][0] / top if top else 0), c.get("created_at") or "", c["id"]

    chosen = max(pool, key=rank)
    return chosen, match[chosen["id"]][1], warn


def candidates(con, activity_id: int) -> list[dict]:
    return [dict(r) for r in con.execute(
        f"SELECT id, kind, text, {db.EN.format('text')} AS text_en, score, created_at FROM bloc_descriptions "
        "WHERE activity_id = ? AND status = 'approved'", (activity_id,))]


def profile_candidates(con, key: str) -> list[dict]:
    """The approved versions of a profile bloc (role, summary, cover_greeting, cover_closing)."""
    return [dict(r) for r in con.execute(
        f"SELECT id, text, {db.EN.format('text')} AS text_en, score, created_at FROM bloc_profile "
        "WHERE key = ? AND status = 'approved'", (key,))]


def profile_text(con, key: str, lang: str = "en", langs=("en", "fr")) -> str:
    """The text a resume uses for a profile bloc: its best version (the summary by its review, the others newest)."""
    chosen, _, _ = best(profile_candidates(con, key), langs, quality=summary_quality if key == "summary" else line_quality)
    return db.tr(chosen["text"], lang) if chosen else ""


_c = lambda i, en, total, fr=None, when="2026-01-01": {
    "id": i, "text": db.i18n(en, fr), "text_en": en, "created_at": when,
    "score": json.dumps({"total": total}) if total is not None else None}
_T = [(re.compile(r"(?<![\w.])react(?![\w])", re.I), 1.5, "react")]
assert best([_c(1, "Built a dashboard", 7), _c(2, "Built it", 5)])[0]["id"] == 1                  # master: quality
assert best([_c(1, "Built a dashboard", 7), _c(2, "Built it in React", 5)], terms=_T)[0]["id"] == 2  # 0.31+0.5 > 0.44
assert best([_c(1, "Built it", 8, "Fait"), _c(2, "Built it well", 8)], ("en", "fr"))[0]["id"] == 1  # French needed
assert best([_c(1, "Built it", 4), _c(2, "Built it in React", None)], terms=_T)[0]["id"] == 1    # unscored left out
assert best([_c(1, "a", None), _c(2, "b", None, when="2026-02-01")])[0]["id"] == 2                # none scored: newest
_s = lambda n, f, a: {"name": {"score": n}, "fame": {"score": f}, "aim": {"score": a}}
assert summary_quality(_s(2, 2, None)) == 1 and summary_quality(_s(1, 1, 1)) == 0.5
