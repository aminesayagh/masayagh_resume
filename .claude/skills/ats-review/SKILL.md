---
name: ats-review
description: Use the resume repo's ATS reviewer tools to check a resume, create a job file from a job posting, match a resume against a posting, or read and act on a review report. Use when the user mentions ATS, a job offer or posting, tailoring the resume, spelling or style of the resume, or checking the PDF.
---

# ATS reviewer

This repo builds tailored resume PDFs (`builder/build_resume.py`) and reviews them against job postings. The reviewer is a **tailoring aid**: it shows what a posting asks for, what the PDF actually says, and what needs a human decision. It never predicts an employer's ATS score or a hiring outcome. Never describe its output as an "ATS score" or a "pass".

All commands run from the repo root with `.venv/bin/python`. Dependencies are in `requirements-review.txt` (`pypdf`, `pyspellchecker`). Every tool has `--help`.

## Files

| Path | What it is | Who edits it |
|---|---|---|
| `content/<slug>.json` | Resume content, the only source of resume text | The user, or you with approval |
| `builder/template/` | Layout only | Don't change the design; parse fixes need the user's approval |
| `output/<slug>.pdf` | Built PDF; this folder holds PDFs only | `builder/build_resume.py` |
| `jobs/<slug>.json` (+ `.txt`) | One posting as structured requirements | You draft it, the user reviews it |
| `analysis/` | Generated reports (JSON and Markdown) | The tools only, never edited by hand |
| `ats/spelling-allow.txt` | Words confirmed correct | Add a word only after the user confirms it |
| `ats/aliases.json` | True synonyms (Postgres = PostgreSQL) | Keep it small; no loose matches |

Use the same slug for the content, PDF and job file of one application: `content/acme-dev.json`, `output/acme-dev.pdf`, `jobs/acme-dev.json`.

## Pipeline

Run these steps in order. Each step writes a report in `analysis/`.

```bash
.venv/bin/python ats/check_spelling.py content/<slug>.json      # 1. spelling: warnings only
.venv/bin/python ats/check_style.py content/<slug>.json         # 2. writing style: warnings only
.venv/bin/python builder/build_resume.py content/<slug>.json        # 3. build output/<slug>.pdf
.venv/bin/python ats/check_pdf.py output/<slug>.pdf             # 4. PDF text: exit 1 on errors
.venv/bin/python ats/check_job.py jobs/<slug>.json              # 5. validate the job file
.venv/bin/python ats/review_ats.py --job jobs/<slug>.json       # 6. full review, runs 1, 2, 4 and matching
```

To review a posting, step 6 is enough. It runs the checks, writes `analysis/<slug>.review.md` and `.review.json`, and finds `output/<slug>.pdf` and `content/<slug>.json` by slug (falling back to `default`). Add `--no-network` when offline. Otherwise the tool opens the LinkedIn, GitHub and website links.

## Creating a job file from a posting

Read `docs/job-file-guide.md` for every field. In short:

1. Save the posting text as `jobs/<slug>.txt` and set `"posting_file": "jobs/<slug>.txt"`.
2. Add one requirement per skill or condition. When one line lists several skills, make one requirement per skill; they share the same `quote`.
3. `quote` must be copied word for word from the posting. Only whitespace may differ.
4. `terms` use the posting's exact wording, and each term must appear in its quote.
5. `priority`: `must_have` only when the posting says so ("Requirements", "must", "at least"). Nice-to-have lines and soft wording ("a plus", "ideally") are `preferred`; the validator rejects them as `must_have`. Responsibilities are usually `preferred`.
6. "At least N years" uses `"kind": "years_experience", "min_years": N` with no terms.
7. Set `"reviewed": false` on everything you draft. Run `ats/check_job.py --draft` until it shows 0 errors. Then **ask the user to review the quotes and priorities**. Only the user sets `"reviewed": true`, or tells you to.

## Reading results

**PDF and content checks:** `error` blocks use (unreadable PDF, missing name or email, image-only page). `warning` is advice, because spelling and style can be correct even when flagged. `info` is context only.

**Matching** gives two results per requirement. Report them separately:

- **Keyword:** `exact` means the posting's term is in the PDF, which recruiter search sees. `alias` means the wording differs, so suggest the posting's term. `absent` means the term is not in the PDF.
- **Evidence:**
  - `met`: found in experience, education, languages or header text.
  - `partial`: found only in the skills list or summary (a claim, not proof), or only some terms are met.
  - `missing`: no supporting text in this PDF. It does **not** mean the user lacks the skill.
  - `uncertain`: the text cannot support a decision.

**Years of experience:** reported two ways, with overlaps counted once and with every job added up. `met` needs the first number to reach the minimum.

**Evidence coverage** is (met + 0.5 × partial) ÷ requirements, per priority. Always present it with its formula, never as an ATS score, and never combined with PDF readability.

## Rules

- **Never invent experience.** Suggestions say what the posting asks for and where the PDF stands. Only add a skill or term to `content/` when the user confirms it is true. "Missing" is information, not a gap to fill.
- **Don't edit `analysis/` by hand.** When a result is wrong, add an override to the job file with `id`, `status`, `reason` and `pdf_quote` (the PDF text the decision relies on, or null). The report keeps the automated finding and flags the override as stale when that quote leaves the PDF. Prefer fixing the resume over overriding.
- **Don't weaken a check to make a report look better.** No loose aliases, no allowlisting words the user hasn't confirmed, and no downgrading errors.
- **After editing content or the template,** rebuild the PDF before re-running `ats/check_pdf.py` or `ats/review_ats.py`. They read the PDF, not the JSON.
- **The user values reports as a record.** Summarize findings, but keep the full list available. Don't trim reports.
- **Tests:** `.venv/bin/python -m unittest discover -s tests -t .`. Run them after changing any tool.

## Known limits

- English spelling only.
- The style rules are text patterns, not judgement.
- Matching is literal plus `ats/aliases.json`. There is no semantic or AI matching, so related wording is missed unless it's an alias.
- LinkedIn often refuses automated link checks, which is reported as "open it in a browser", not as broken.
- The section split depends on the template headings. If the headings change, `check_pdf.template_headings` picks them up from `builder/template/resume.html`.
