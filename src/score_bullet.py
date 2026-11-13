"""Score each experience line (bloc_descriptions) with the user's bullet rubric, one Haiku call per line.

Rubric (XYZ formula: accomplished X, as measured by Y, by doing Z), each criterion 0 missing / 1 partial / 2 clear:
  result: what improved or became possible · evidence: a metric, adoption, milestone or concrete scope ·
  contribution: what the candidate built, designed, changed or led · clarity: the point is clear on first read.
Haiku fills in the classifier part: the scores, the exact phrase behind each nonzero score, the diagnostics
(evidence_type, claim_evidence_match, attribution) and revision requests. The code adds the rest, so the model
never decides it: total /8, verdict (Ready when result, contribution and clarity are 2, evidence >= 1 and the
match is 'supports'; else Revise) and a check that each quoted phrase is really in the line.
Stored as JSON in bloc_descriptions.score with the text's hash; a line whose English text changed is re-scored.
Target-role relevance and overlap need a posting or several lines, so they're not part of the per-line score.

Usage: .venv/bin/python src/score_bullet.py pending        # score new or changed lines (also run by db_sync)
       .venv/bin/python src/score_bullet.py show           # every line with its total and verdict
Needs: the `claude` CLI, logged in. Each scored line is one Haiku call on the user's subscription.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import date
from typing import Literal

from pydantic import BaseModel

import db
from db import EN, tr

MODEL = "claude-haiku-5-5"  # the user asked for Haiku 5.5 by name
VERSION = 1  # bump when the prompt or rubric changes: every line is then re-scored by `pending`
Score = Literal[0, 1, 2]


class Phrases(BaseModel):
    result: str | None
    evidence: str | None
    contribution: str | None
    clarity: str | None


class Scores(BaseModel):
    result: Score
    evidence: Score
    contribution: Score
    clarity: Score


class Classified(BaseModel):
    scores: Scores
    supporting_phrases: Phrases
    evidence_type: Literal["measured_impact", "adoption", "delivery", "scope", "none"]
    claim_evidence_match: Literal["supports", "partial", "mismatch", "missing"]
    attribution: Literal["individual", "team_with_clear_role", "unclear"]
    revision_requests: list[str]


PROMPT = """Score one resume experience line with this rubric. Score only what the line states; the job title only
helps interpret terminology.

Each criterion 0 (missing), 1 (partial) or 2 (clear):
- result: 0 states a duty or activity; 1 names a deliverable or a vague improvement; 2 explains what improved, what
  became possible, or why the delivery mattered.
- evidence: 0 no concrete detail about the result; 1 an observable detail, such as a production rollout, with limited
  context; 2 a meaningful metric, adoption count, milestone, or concrete scope that lets the reader judge the result.
- contribution: 0 the candidate's action is unclear; 1 broad wording such as "helped develop"; 2 names what the
  candidate built, designed, changed, or led.
- clarity: 0 the main point is hard to identify; 1 it takes a reread or depends on unexplained jargon; 2 a reader
  grasps the main point on the first read.

supporting_phrases: for each nonzero score, the exact phrase copied from the line that justifies it; null for a zero.
evidence_type: measured_impact, adoption, delivery, scope, or none.
claim_evidence_match: supports, partial, mismatch, or missing. A rollout to four teams supports an adoption claim; a
claim about faster reporting needs evidence about reporting speed. With several material claims, use the weakest match.
attribution: individual, team_with_clear_role, or unclear (for a team result, is the candidate's own action identifiable?).
revision_requests: one concrete request per failed check (score below 2, or a match other than supports). Say what to
add or change; never invent facts, numbers or names, and never write a rewritten line.

Example. Line: "Built a campaign dashboard in React."
{{"scores": {{"result": 1, "evidence": 0, "contribution": 2, "clarity": 2}},
 "supporting_phrases": {{"result": "a campaign dashboard", "evidence": null,
   "contribution": "Built a campaign dashboard in React", "clarity": "Built a campaign dashboard in React"}},
 "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual",
 "revision_requests": ["State what users could do with the dashboard.",
   "Add a verified adoption, rollout, or scope detail tied to that capability."]}}

Job title: {role}
Line: {text}"""


def classify(text: str, role: str) -> Classified:
    """One Haiku call through the Claude Code CLI (its login, no API key); same call shape as parse_offer."""
    cmd = ["claude", "-p", "--model", MODEL, "--output-format", "json",
           "--json-schema", json.dumps(Classified.model_json_schema()),
           "--system-prompt", "You score resume bullets against a fixed rubric and return JSON only.",
           "--tools", "", "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence"]
    run = subprocess.run(cmd, input=PROMPT.format(role=role or "unknown", text=text), capture_output=True, text=True,
                         cwd=tempfile.gettempdir(), timeout=300)
    out = json.loads(run.stdout or "{}")
    if run.returncode or out.get("is_error") or not out.get("structured_output"):
        raise RuntimeError(f"claude CLI failed: {run.stderr.strip() or out.get('result')}")
    return Classified.model_validate(out["structured_output"])


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def verdict(c: dict, text: str) -> dict:
    """The parts the code decides: total, Ready/Revise (the user's approval rule) and the quote check."""
    s = c["scores"]
    ready = (s["result"] == s["contribution"] == s["clarity"] == 2 and s["evidence"] >= 1
             and c["claim_evidence_match"] == "supports")
    unquoted = [k for k, p in c["supporting_phrases"].items()
                if p and " ".join(p.split()).casefold() not in " ".join(text.split()).casefold()]
    return {"total": sum(s.values()), "verdict": "Ready" if ready else "Revise", "unquoted_phrases": unquoted}


def score(text: str, role: str) -> dict:
    c = classify(text, role).model_dump()
    return {**c, **verdict(c, text), "model": MODEL, "version": VERSION, "text_hash": text_hash(text),
            "scored_at": date.today().isoformat()}


def lines(con) -> list:
    return con.execute(f"SELECT d.id, {EN.format('d.text')} AS text, d.score, e.role FROM bloc_descriptions d "
                       "JOIN bloc_activities a ON a.id = d.activity_id JOIN bloc_experiences e ON e.id = a.experience_id "
                       "ORDER BY d.id").fetchall()


def stale(row) -> bool:
    old = json.loads(row["score"]) if row["score"] else None
    return not old or old.get("version") != VERSION or old.get("text_hash") != text_hash(row["text"])


def pending(con=None) -> int:
    """Score every line that has no score, or whose text or rubric version changed. A failed call leaves the line
    unscored (warned), so the next run retries it. Returns how many were scored."""
    if os.environ.get("RESUME_NO_SCORING"):  # set by the tests: they must never call the model
        return 0
    con = con or db.connect()
    done = 0
    for row in [r for r in lines(con) if stale(r)]:
        try:
            result = score(row["text"], tr(row["role"]))
        except (RuntimeError, ValueError, subprocess.TimeoutExpired) as e:
            print(f"score_bullet: line {row['id']} not scored ({e}); `score_bullet.py pending` retries it")
            continue
        con.execute("UPDATE bloc_descriptions SET score = ? WHERE id = ?", (json.dumps(result, ensure_ascii=False), row["id"]))
        con.commit()  # one line at a time: an interrupted run keeps what it scored
        done += 1
        print(f"score_bullet: line {row['id']} {result['total']}/8 {result['verdict']}")
    if done:
        db.dump(con)
    return done


def show(con=None) -> None:
    for row in lines(con or db.connect()):
        sc = json.loads(row["score"]) if row["score"] else None
        mark = f"{sc['total']}/8 {sc['verdict']:6}" if sc else "unscored  "
        print(f"{row['id']:>4} {mark} {row['text'][:90]}")


assert verdict({"scores": {"result": 1, "evidence": 0, "contribution": 2, "clarity": 2}, "claim_evidence_match": "missing",
                "supporting_phrases": {"result": "a campaign dashboard", "evidence": None, "contribution": "Built a campaign "
                "dashboard in React", "clarity": "x"}}, "Built a campaign dashboard in React.") == \
    {"total": 5, "verdict": "Revise", "unquoted_phrases": ["clarity"]}  # the rubric's own example: 5/8 · Revise

if __name__ == "__main__":
    if sys.argv[1:] == ["pending"]:
        print(f"Scored {pending()} line(s)")
    elif sys.argv[1:] == ["show"]:
        show()
    else:
        sys.exit(__doc__)
