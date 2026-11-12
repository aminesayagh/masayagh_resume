"""Parse a job posting: offer fields + typed skills per phrase.

1. Code splits the posting into phrases (lines, bullets, sentences).
2. One Claude Haiku call (via the `claude` CLI, no API key) reads the numbered phrases:
   company, title, location, spoken languages, and the skills each phrase asks for,
   each typed technical, design, ai, soft, language, location, education or none,
   with priority (100 must-have, 0 preferred) and min_years (or null).
   Phrases without skills are typed none.

Usage: .venv/bin/python src/parse_offer.py POSTING.txt   (or pipe the text on stdin)
       .venv/bin/python src/parse_offer.py --selftest     (phrase splitter check, no model)
Needs: the `claude` CLI, logged in.
Cache: results are kept in data/cache/parse_offer/ (git-ignored), keyed on the phrases
       and the whole recipe; nothing to manage, delete the folder any time.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

HAIKU = "haiku"  # Claude Code alias for the latest Haiku
EFFORT = "low"   # same accuracy as default on the 100 samples, ~30% faster
CACHE = Path(__file__).resolve().parent.parent / "data" / "cache" / "parse_offer"

TYPES = {
    "technical": "Hard or professional skill: programming language, framework, tool, platform, database, "
                 "method, or a non-software trade skill (e.g. Java, Kubernetes, SQL, CI/CD, Excel, accounting)",
    "design": "Design skill or tool: UI, UX, visual, interaction or product design (e.g. Figma, wireframing)",
    "ai": "AI, machine learning or data science skill (e.g. LLMs, RAG, PyTorch, generative AI, NLP)",
    "soft": "Interpersonal or work trait (e.g. communication, leadership, autonomy, teamwork)",
    "language": "Spoken or written human language (e.g. English, French); never a programming language",
    "location": "Place of work, work arrangement or mobility (e.g. Paris, remote, hybrid, relocation)",
    "education": "Degree, diploma, school level or certification (e.g. Master's degree, Bac+5, AWS certification)",
    "none": "Not a skill asked of the candidate (e.g. a benefit, a perk, the company's product, "
            "a bare duration like 5+ years)",
}


class Skill(BaseModel):
    name: str
    type: Literal["technical", "design", "ai", "soft", "language", "location", "education", "none"]
    required: bool           # False when the posting marks it as a plus / nice to have
    min_years: int | None    # years of experience asked for this skill, if stated


class PhraseSkills(BaseModel):
    phrase: int          # index in the numbered phrase list
    skills: list[Skill]


class Offer(BaseModel):
    company: str | None
    title: str | None
    location: str | None
    languages: list[str]
    phrases: list[PhraseSkills]


PROMPT = """Below is a job posting split into numbered phrases.

Return:
- company: the hiring company exactly as written (not a client or partner), or null
- title: the job title exactly as written (keep "H/F", "(m/w/d)"), or null
- location: the main place of work exactly as written, or null
- languages: spoken languages the posting asks for (required or a plus), as English names ("French", not "français"); programming languages never count
- phrases: for every phrase that asks something of the candidate, its number and the skills it names. A skill name is a short term (1-4 words) copied from the phrase: a technology, method, trait, spoken language, degree, or work location/arrangement. Leave out phrases that ask nothing.
- each skill's type, judged in the context of its phrase:
{types}
- each skill's required: false when the posting presents it as optional ("a plus", "nice to have", "ideally", "bonus", "apprécié", "un plus", "idéalement"); true otherwise, including skills named in responsibilities
- each skill's min_years: the minimum years of experience the phrase asks for that skill ("5+ years of backend experience in Python" -> 5 for both "backend experience" and "Python"; "3 à 5 ans" -> 3), else null. A duration is never a skill by itself.

Phrases:
{phrases}"""


def phrases(text: str) -> list[str]:
    """Lines and bullets, then sentences; bullet marks and blanks dropped."""
    out = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*•·▪◦–]|\d+[.)])\s*", "", line).strip()
        out += [s.strip() for s in re.split(r"(?<=[.!?;])\s+(?=[A-ZÀ-Ý])", line) if s.strip()]
    return out


def extract(items: list[str]) -> Offer:
    """One Haiku call through the Claude Code CLI (uses its login, no API key)."""
    prompt = PROMPT.format(
        types="\n".join(f"  - {k}: {v}" for k, v in TYPES.items()),
        phrases="\n".join(f"{i}. {p}" for i, p in enumerate(items)),
    )
    cmd = [
        "claude", "-p", "--model", HAIKU, "--effort", EFFORT, "--output-format", "json",
        "--json-schema", json.dumps(Offer.model_json_schema()),
        "--system-prompt", "You extract structured data from job postings.",
        # no tools, settings, plugins, MCP or saved session: a plain model call
        "--tools", "", "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
    ]
    run = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                         cwd=tempfile.gettempdir(), timeout=300)
    out = json.loads(run.stdout or "{}")
    if run.returncode or out.get("is_error") or not out.get("structured_output"):
        raise RuntimeError(f"claude CLI failed: {run.stderr.strip() or out.get('result')}")
    return Offer.model_validate(out["structured_output"])


def skill(s: Skill) -> dict:
    """Skill as stored: priority 100 = must-have, 0 = preferred (the db's 0-100 scale)."""
    return {"name": s.name, "type": s.type, "priority": 100 if s.required else 0, "min_years": s.min_years}


def cache_key(items: list[str]) -> str:
    """Same phrases + same prompt, types, schema and model -> same key.
    Any change to the prompt or settings gives new keys, so old entries are simply never read."""
    recipe = [items, PROMPT, TYPES, Offer.model_json_schema(), HAIKU, EFFORT]
    return hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()


def parse(text: str) -> dict:
    """Parse a posting; a posting already parsed with the same recipe is read from data/cache/."""
    items = phrases(text)
    path = CACHE / f"{cache_key(items)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    offer = extract(items)
    skills = {p.phrase: p.skills for p in offer.phrases if p.skills}
    result = {
        "company": offer.company,
        "title": offer.title,
        "location": offer.location,
        "languages": offer.languages,
        "phrases": [
            {"text": phrase, "skills": [skill(s) for s in skills[i]]} if i in skills
            else {"text": phrase, "type": "none", "skills": []}
            for i, phrase in enumerate(items)
        ],
    }
    # ponytail: one file per posting, never pruned; delete data/cache/ any time to reclaim space
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    return result


def _selftest():
    got = phrases("About us\n- Strong Python skills. Docker is a plus!\n• Anglais courant\n\n2) Bac+5 required")
    assert got == ["About us", "Strong Python skills.", "Docker is a plus!", "Anglais courant", "Bac+5 required"], got
    assert phrases("Based in Paris, e.g. hybrid.") == ["Based in Paris, e.g. hybrid."]
    # whitespace and bullet differences hit the same cache entry; different content does not
    assert cache_key(phrases("- Python\n\n  Docker")) == cache_key(phrases("Python\nDocker"))
    assert cache_key(phrases("Python")) != cache_key(phrases("Java"))
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
        print(json.dumps(parse(text), indent=2, ensure_ascii=False))
