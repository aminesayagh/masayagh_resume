"""Parse a job posting: offer fields + typed skills per phrase.

1. Code splits the posting into phrases (lines, bullets, sentences).
2. One Claude Haiku call (via the `claude` CLI, no API key) reads the numbered phrases:
   company, title, location, spoken languages, and the skills each phrase asks for,
   each typed technical, design, ai, soft, language, location, education or none.
   Phrases without skills are typed none.

Usage: .venv/bin/python src/parse_offer.py POSTING.txt   (or pipe the text on stdin)
       .venv/bin/python src/parse_offer.py --selftest     (phrase splitter check, no model)
Needs: the `claude` CLI, logged in.
"""
import json
import re
import subprocess
import sys
import tempfile
from typing import Literal

from pydantic import BaseModel

HAIKU = "haiku"  # Claude Code alias for the latest Haiku

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
        "claude", "-p", "--model", HAIKU, "--output-format", "json",
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


def parse(text: str) -> dict:
    items = phrases(text)
    offer = extract(items)
    skills = {p.phrase: p.skills for p in offer.phrases if p.skills}
    return {
        "company": offer.company,
        "title": offer.title,
        "location": offer.location,
        "languages": offer.languages,
        "phrases": [
            {"text": phrase, "skills": [s.model_dump() for s in skills[i]]} if i in skills
            else {"text": phrase, "type": "none", "skills": []}
            for i, phrase in enumerate(items)
        ],
    }


def _selftest():
    got = phrases("About us\n- Strong Python skills. Docker is a plus!\n• Anglais courant\n\n2) Bac+5 required")
    assert got == ["About us", "Strong Python skills.", "Docker is a plus!", "Anglais courant", "Bac+5 required"], got
    assert phrases("Based in Paris, e.g. hybrid.") == ["Based in Paris, e.g. hybrid."]
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
        print(json.dumps(parse(text), indent=2, ensure_ascii=False))
