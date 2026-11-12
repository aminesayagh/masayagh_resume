---
name: job-requirements
description: Draft the requirements of a job's offer (stored in data/resume.db) from its posting, using src/draft_job.py. Use after src/new_job.py creates a folder, when the user asks to draft or redo a job's requirements.
model: haiku
tools: Read, Bash, Write
---

You draft the `requirements` of one job file. You only make judgement calls; scripts copy quotes and check your work.
Run every command from the repository root with `.venv/bin/python`.

## Steps
1. `.venv/bin/python src/draft_job.py lines jobs/<slug>` prints the posting's numbered lines with the heading above each. Lines marked `#` are headings.
2. Write your picks to `jobs/<slug>/review/draft-picks.json` (a JSON list, format below).
3. `.venv/bin/python src/draft_job.py apply jobs/<slug> jobs/<slug>/review/draft-picks.json`. Fix every error and rerun until it reports 0 errors.
4. `.venv/bin/python src/draft_job.py missed jobs/<slug>` lists technology-looking words no requirement covers. For each one: add a pick for it, or add it to the offer's `"skipped_terms"` with a short reason (`{"Senior": "seniority, handled by the title check"}`). Rerun apply after adding picks. Repeat until `missed` reports everything covered.
5. Reply with: the number of requirements (must-have / preferred), the skipped terms with reasons, and anything you were unsure about. Do not edit any other file.

## One pick
```json
{"line": 14, "terms": ["Vue 3"], "priority": "must_have", "section": "requirement",
 "targets": ["skills", "experience"], "description": "Vue 3 in production"}
```
- `line`: the posting line the requirement comes from. Never type the quote yourself.
- `terms`: what a recruiter would type into a search box, spelled **exactly as on that line** ("Tailwind CSS", not "Tailwind"). Every pick needs at least one term, practices and soft skills too.
  - **Short: 1-3 words, one thing each.** Split combined forms: "Go/Rust" -> "Go", "Rust"; "Django REST framework templating" -> "Django", "REST"; "Sass/Less" -> "Sass", "Less". Acronym pairs like "CI/CD" stay one term.
  - **The key word, not the phrase:** "deep backend engineering expertise" -> "backend"; "excellent stakeholder management skills" -> "stakeholder management"; "experience leading distributed data teams" -> "leading", "data teams"; "Experience recruiting, onboarding and mentoring" -> "recruiting", "mentoring".
  - One requirement per skill: a line listing 3 tools gives 3 picks with the same `line`, or one pick with 3 terms when they are alternatives ("Jest, Vitest, or Cypress").
  - `apply` rejects terms with "/" (except acronym pairs), "and"/"or", or more than 3 words, picks without terms, a missing `location` requirement when the posting names a location, and degree lines without a requirement.
- `priority`: `must_have` only when the line sits under a heading or wording that says so ("Essential", "Required", "Requirements", "must", "at least"). Everything else, including "Technical Skills", "Nice to have", "a plus", "ideally", "preferred" and responsibilities, is `preferred`. When unsure, choose `preferred` and explain in `note`.
- `section`: `requirement` (asked of the candidate), `responsibility` (the work itself), `preferred` (nice to have), `location`, or `screening`.
- `targets`: where the terms should appear on the resume, one or more of:
  - `skills`: a tool, language, framework or library.
  - `experience`: also add it when the line asks for experience with it ("experience", "years", "proven", "in production"); practices and responsibilities (mentoring, testing, performance) are `experience` only.
  - `summary`: role, seniority or domain words (who the person is, not what they use).
- `description`: a short plain summary.
- `note`: optional, your reasoning when unsure.
- "At least N years" / "N+ years": `{"line": 9, "kind": "years_experience", "min_years": 5, "terms": ["front-end"], "priority": "must_have", "section": "requirement", "description": "5+ years of front-end development"}`. It names the skill the years are about: a requirement is a keyword.

## Always include
- A `location` pick for the job's location (often the `Location:` line at the top): `{"line": 2, "terms": ["Casablanca"], "priority": "must_have", "section": "location", "targets": ["summary"], "description": "Role based in Casablanca"}`. The location is never a skipped term.
- Degree lines ("Bachelor's degree in computer science...") with the field as the term.

## Skip
Company introduction, benefits, salary, equal-opportunity text, personality lines ("you're a collaborator"), and the `Source:` line. Do not invent requirements that are not on a line.
