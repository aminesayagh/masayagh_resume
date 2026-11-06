---
name: ats-review
description: Use the resume repo's ATS reviewer tools to check a resume, create a job file from a job posting, match a resume against a posting, or read and act on a review report. Use when the user mentions ATS, a job offer or posting, tailoring the resume, spelling or style of the resume, or checking the PDF.
---

# ATS reviewer

This repo builds tailored resume PDFs (`src/build_resume.py`) and reviews them against job postings. The reviewer is a **tailoring aid**: it shows what a posting asks for, what the PDF actually says, and what needs a human decision. It never predicts an employer's ATS score or a hiring outcome. Never describe its output as an "ATS score" or a "pass".

All commands run from the repo root with `.venv/bin/python`. Dependencies are in `requirements-review.txt` (`pypdf`, `pyspellchecker`). Every tool has `--help`.

## Files

Everything for one application lives together in one `jobs/` subfolder, named `<company>-<title>-v<N>` (e.g. `jobs/acme-backend-engineer-v1/`).

| Path | What it is | Who edits it |
|---|---|---|
| `template/default.json` | Master resume content | The user, or you with approval |
| `template/resume.html`, `template/assets/`, `template/fonts/` | Layout only | Don't change the design; parse fixes need the user's approval |
| `template/resume.pdf` | Baseline PDF built from `default.json` | `src/build_resume.py` |
| `jobs/<slug>/posting.txt` | The pasted job posting text | Written once when the folder is created |
| `jobs/<slug>/job.json` | One posting as structured requirements | You draft it, the user reviews it |
| `jobs/<slug>/content.json` | Tailored resume content for this application, starts as a copy of `template/default.json` | The user, or you with approval |
| `jobs/<slug>/resume.pdf` | Built PDF for this application | `src/build_resume.py` |
| `jobs/<slug>/review.json`, `review.md` | Generated report | The tools only, never edited by hand |
| `src/spelling-allow.txt` | Words confirmed correct | Add a word only after the user confirms it |
| `src/aliases.json` | True synonyms (Postgres = PostgreSQL) | Keep it small; no loose matches |

`src/new_job.py` scaffolds a new `jobs/<slug>/` folder interactively (company, job title, pasted posting). It **refuses to run** if `template/default.json` has any unresolved spelling/style/PDF-readability finding (warning or error) — fix the baseline first, so every new application starts clean. Run `src/check_template.py` on its own anytime to see that same list without starting a new application.

## Pipeline

Each tool defaults to its input's own folder: run against `template/default.json` for the baseline, or a `jobs/<slug>/` file for one application. Each step writes its report next to its input.

```bash
.venv/bin/python src/check_template.py                        # is template/ ready? lists findings, exit 1 if not
.venv/bin/python src/new_job.py                               # 0. scaffold jobs/<slug>/ (blocks if template/ has findings)
.venv/bin/python src/check_spelling.py jobs/<slug>/content.json   # 1. spelling: warnings only
.venv/bin/python src/check_style.py jobs/<slug>/content.json      # 2. writing style: warnings only
.venv/bin/python src/build_resume.py jobs/<slug>/content.json     # 3. build jobs/<slug>/resume.pdf
.venv/bin/python src/check_pdf.py jobs/<slug>/resume.pdf           # 4. PDF text: exit 1 on errors
.venv/bin/python src/check_job.py jobs/<slug>/job.json             # 5. validate the job file
.venv/bin/python src/review_ats.py --job jobs/<slug>/job.json      # 6. full review, runs 1, 2, 4 and matching
```

`src/new_job.py` already runs 1, 2, 3 and a partial version of 6 (no matching yet, since `job.json` has empty `requirements`). To review a posting once requirements are drafted, step 6 is enough: it finds `resume.pdf` and `content.json` next to the job file. Add `--no-network` when offline. Otherwise the tool opens the LinkedIn, GitHub and website links.

## Creating a job file from a posting

`src/new_job.py` creates the folder, `posting.txt`, a `job.json` skeleton (empty `requirements`) and a partial report. Read `docs/job-file-guide.md` for every requirement field. In short:

1. `job.json`'s `"posting_file"` already points at `jobs/<slug>/posting.txt`.
2. Add one requirement per skill or condition. When one line lists several skills, make one requirement per skill; they share the same `quote`.
3. `quote` must be copied word for word from the posting. Only whitespace may differ.
4. `terms` use the posting's exact wording, and each term must appear in its quote.
5. `priority`: `must_have` only when the posting says so ("Requirements", "must", "at least"). Nice-to-have lines and soft wording ("a plus", "ideally") are `preferred`; the validator rejects them as `must_have`. Responsibilities are usually `preferred`.
6. "At least N years" uses `"kind": "years_experience", "min_years": N` with no terms.
7. Set `"reviewed": false` on everything you draft. Run `src/check_job.py jobs/<slug>/job.json --draft` until it shows 0 errors. Then **ask the user to review the quotes and priorities**. Only the user sets `"reviewed": true`, or tells you to. Then rerun `src/review_ats.py --job jobs/<slug>/job.json` to fill in the matching section and evidence coverage.

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

- **Never invent experience.** Suggestions say what the posting asks for and where the PDF stands. Only add a skill or term to a `content.json` when the user confirms it is true. "Missing" is information, not a gap to fill.
- **Don't edit a `review.json`/`review.md` (or any generated report) by hand.** When a result is wrong, add an override to the job file with `id`, `status`, `reason` and `pdf_quote` (the PDF text the decision relies on, or null). The report keeps the automated finding and flags the override as stale when that quote leaves the PDF. Prefer fixing the resume over overriding.
- **Don't weaken a check to make a report look better.** No loose aliases, no allowlisting words the user hasn't confirmed, and no downgrading errors.
- **`template/default.json` must stay clean.** `src/new_job.py` blocks creating a new job folder while the baseline has any spelling/style/PDF-readability finding (warning or error), because every new application starts from it. Fix the baseline before scaffolding; don't bypass the gate.
- **After editing content or the template,** rebuild the PDF before re-running `src/check_pdf.py` or `src/review_ats.py`. They read the PDF, not the JSON.
- **The user values reports as a record.** Summarize findings, but keep the full list available. Don't trim reports.
- **Tests:** `.venv/bin/python -m unittest discover -s tests -t .`. Run them after changing any tool.

## Known limits

- English spelling only.
- The style rules are text patterns, not judgement.
- Matching is literal plus `src/aliases.json`. There is no semantic or AI matching, so related wording is missed unless it's an alias.
- LinkedIn often refuses automated link checks, which is reported as "open it in a browser", not as broken.
- The section split depends on the template headings. If the headings change, `check_pdf.template_headings` picks them up from `template/resume.html`.
