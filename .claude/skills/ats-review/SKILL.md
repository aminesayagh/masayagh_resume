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
| `jobs/<slug>/<pdf_name>` | Built PDF for this application, named by `job.json`'s `pdf_name` (your name, job title, company) | `src/build_resume.py` |
| `template/default-cover.json`, `template/cover-letter.html` | Default cover letter text and its layout | The user, or you with approval |
| `jobs/<slug>/cover.json` | This job's cover letter text, created from `default-cover.json` on the first build | You, only when the user asks (`.claude/skills/draft-cover-letter/SKILL.md`) |
| `jobs/<slug>/<stem>-Cover-Letter.pdf`, `<stem>-Resume-and-Cover-Letter.pdf` | Cover letter alone, and resume + cover letter in one file; rebuilt with every resume build | `src/build_cover.py` (run it alone after editing `cover.json`) |
| `jobs/<slug>/review.json`, `review.md`, `interview.json`, `dashboard.html` | Generated report, interview prep sheet and one-page overview | The tools only, never edited by hand |
| `src/spelling-allow.txt` | Words confirmed correct | Add a word only after the user confirms it, via `check_spelling.py --add` |
| `src/aliases.json` | True synonyms (Postgres = PostgreSQL) | Keep it small; no loose matches |

`src/new_job.py` scaffolds a new `jobs/<slug>/` folder interactively (company, job title, pasted posting). It **refuses to run** if `template/default.json` has any unresolved spelling/style/PDF-readability finding (warning or error) — fix the baseline first, so every new application starts clean. Run `src/check_template.py` on its own anytime to see that same list without starting a new application.

## Pipeline

Each tool defaults to its input's own folder: run against `template/default.json` for the baseline, or a `jobs/<slug>/` file for one application. Each step writes its report next to its input.

```bash
.venv/bin/python src/check_template.py                        # is template/ ready? lists findings, exit 1 if not
.venv/bin/python src/new_job.py --url JOB_URL                  # 0. scaffold jobs/<slug>/ from a link (blocks if template/ has findings)
.venv/bin/python src/new_job.py --company X --title Y --posting FILE   #    or from pasted text when the site blocks reading
.venv/bin/python src/check_spelling.py jobs/<slug>/content.json   # 1. spelling: warnings only
.venv/bin/python src/check_style.py jobs/<slug>/content.json      # 2. writing style: warnings only
.venv/bin/python src/build_resume.py jobs/<slug>/content.json     # 3. build jobs/<slug>/<pdf_name>
.venv/bin/python src/check_pdf.py jobs/<slug>/<pdf_name>           # 4. PDF text: exit 1 on errors
.venv/bin/python src/check_job.py jobs/<slug>/job.json             # 5. validate the job file
.venv/bin/python src/review_ats.py --job jobs/<slug>/job.json --preview  # match per term, writes nothing, drafts OK
.venv/bin/python src/review_ats.py --job jobs/<slug>/job.json      # 6. full review, runs 1, 2, 4 and matching
.venv/bin/python src/publish_resume.py jobs/<slug>/job.json        # 7. push the PDF to the portfolio (main)
```

**From a link:** `src/fetch_posting.py URL` prints what it can read (title, company, location vs the user's, description) without creating anything. It reads schema.org JobPosting data, the Greenhouse API, schema.org microdata (SAP SuccessFactors), the Oracle Recruiting Cloud API, or the page rendered in Chrome. Works with LinkedIn, Greenhouse, Lever, careers.oracle.com and Capgemini; when a site blocks it, ask the user to paste the posting. `new_job.py --url` stores `url`, `location` and `location_match` in `job.json`; tell the user the location verdict.

**After any edit to a job's `content.json`, run `src/tailor.py jobs/<slug>`:** it builds (which refreshes the review, interview prep and dashboard), publishes unless the PDF is over 3 pages or has errors, and prints the full table of everything not met. **Show that table to the user as printed, before any comment;** never summarize or drop rows.

**Years of experience per skill:** `template/skills.json` holds every resume skill, its posting synonyms (`match`) and the user's start date; years are computed to today. Each dashboard has a "Skills for application forms" box ready to paste. After adding skills to any `content.json`, run `src/skills_inventory.py sync`, then `missing`, and **ask the user for each start date** (never guess); record with `src/skills_inventory.py set "<skill>" YYYY-MM`.

**Not ready = `_` prefix:** a job PDF over 3 pages or with a broken skills layout is saved as `_<pdf_name>` and the ready-named file is removed. `publish_resume.py` refuses it and the dashboard labels it "NOT READY, do not send". Never rename it by hand; fix the content and rebuild.

**Every job PDF build refreshes the review:** `src/build_resume.py jobs/<slug>/content.json` re-runs the review (no network), prints what changed since the previous report with a verdict, and saves `review.md`/`review.json`, `interview.json` and `dashboard.html`. The dashboard is therefore never older than the PDF. (Skipped for the template, for `-o` builds and before requirements exist.)

**While tailoring,** use `--preview` after each rebuild instead of ad-hoc scripts: it lists every term's status and the PDF line it matched, then compares with the saved `review.json` and ends with a verdict (`no regression`, or `REGRESSION:` with what got worse). Report that verdict to the user after each change; rerun without `--preview` to save the new baseline once they accept it. `build_resume.py` warns when the PDF goes over 3 pages and prints the start of the last page, so you know what spilled. Add confirmed spellings with `src/check_spelling.py --add WORD`, never by editing `src/spelling-allow.txt` by hand. After a template change, `src/check_template.py` lists job folders that are still untouched template copies (`job.json`'s `template_sha`); those are safe to refresh with `cp template/default.json`, rebuild and publish.

**Dashboard:** `jobs/<slug>/dashboard.html` gives the full picture of one offer (location check, links, coverage, requirements with posting quotes and resume lines, interview prep, full posting). `review_ats.py` and `new_job.py` rebuild it; `src/dashboard.py [jobs/<slug>]` rebuilds one or all. Open it from WSL with `explorer.exe "$(wslpath -w jobs/<slug>/dashboard.html)"`.

**Publishing (step 7):** run it after every rebuild of a job's PDF. Details and rules: [`../publish-resume/SKILL.md`](../publish-resume/SKILL.md).

`src/new_job.py` already runs 1, 2, 3 and a partial version of 6 (no matching yet, since `job.json` has empty `requirements`). To review a posting once requirements are drafted, step 6 is enough: it finds the PDF (`job.json`'s `pdf_name`) and `content.json` next to the job file. Add `--no-network` when offline. Otherwise the tool opens every web link in the PDF (contact, projects, badges; redirects followed). `src/check_template.py` always does, so a broken link (HTTP 4xx/5xx) blocks `new_job.py`; being offline is only a note.

## Creating a job file from a posting

`src/new_job.py` creates the folder, `posting.txt`, a `job.json` skeleton (empty `requirements`) and a partial report.

**Draft with the `job-requirements` agent** (`.claude/agents/job-requirements.md`, runs on Haiku to save cost). It uses `src/draft_job.py`: `lines` numbers the posting, `apply` builds requirements from line numbers (the script copies quotes, so they're always verbatim), `missed` lists technology-looking words no requirement covers, which the agent must cover or record in `"skipped_terms"` with a reason. Check its result against the rules below before showing the user. Read `docs/job-file-guide.md` for every requirement field. In short:

1. `job.json`'s `"posting_file"` already points at `jobs/<slug>/posting.txt`.
2. Add one requirement per skill or condition. When one line lists several skills, make one requirement per skill; they share the same `quote`.
3. `quote` must be copied word for word from the posting. Only whitespace may differ.
4. `terms` use the posting's exact wording, and each term must appear in its quote.
5. `priority`: `must_have` only when the posting says so ("Requirements", "must", "at least"). Nice-to-have lines and soft wording ("a plus", "ideally") are `preferred`; the validator rejects them as `must_have`. Responsibilities are usually `preferred`.
6. "At least N years" uses `"kind": "years_experience", "min_years": N` with no terms.
6b. `targets`: where the terms belong on the resume, one or more of `summary` (role, seniority, domain), `skills` (tools, languages, frameworks), `experience` (anything the posting asks experience with; practices and responsibilities). The review then reports **placement gaps**: a targeted section where the term isn't found yet.
7. Set `"reviewed": false` on everything you draft. Run `src/check_job.py jobs/<slug>/job.json --draft` until it shows 0 errors. Then **ask the user to review the quotes and priorities**. Only the user sets `"reviewed": true`, or tells you to. Right after drafting, run `src/review_ats.py --job jobs/<slug>/job.json` anyway: it saves the full report, `interview.json` and the dashboard, labelled **draft** while requirements are unreviewed. Rerun after the user approves to drop the label.

## Reading results

**PDF and content checks:** `error` blocks use (unreadable PDF, missing name or email, image-only page). `warning` is advice, because spelling and style can be correct even when flagged. `info` is context only.

**Job title:** the review warns when `content.json`'s `role` differs from the posting's title (from `job.json`'s "Company — Title"). Tell the user, and propose the posting's title only if it truthfully describes them.

**Matching** gives two results per requirement. Report them separately:

- **Keyword:** `exact` means the posting's term is in the PDF, which recruiter search sees. `alias` means the wording differs, so suggest the posting's term. `absent` means the term is not in the PDF.
- **Evidence:**
  - `met`: found in experience, education, languages or header text.
  - `partial`: found only in the skills list or summary (a claim, not proof), or only some terms are met.
  - `missing`: no supporting text in this PDF. It does **not** mean the user lacks the skill.
  - `uncertain`: the text cannot support a decision.

**Years of experience:** reported two ways, with overlaps counted once and with every job added up. `met` needs the first number to reach the minimum.

**Evidence coverage** is (met + 0.5 × partial) ÷ requirements, per priority. Always present it with its formula, never as an ATS score, and never combined with PDF readability.

## Tailoring a job resume on the user's behalf

When the user asks you to update a job's `content.json` from the review results, these limits apply. Anything outside them needs the user's permission first.

**Layout**
- The resume is always **exactly 3 pages**. If a change pushes it to 4, shorten or swap content within these rules, or ask. Never publish a 4-page resume.
- Skills have **exactly 6 rows**, in this order, and nothing else is accepted:
  1. programming languages
  2. development technologies
  3. development technologies
  4. development technologies
  5. design tools
  6. AI
- The **number of skills shown stays the same** as in `template/default.json`, in total and per row. You may replace skills, never add extra ones.
- A skill is a language, framework, library or tool. Practices and qualities ("Performance optimisation", "Communication") are not skills; don't put them in the list.

**Experience: propose, then wait for confirmation**
- Start from the review's **placement gaps** with `experience` in "missing from". For each, write a proposal and show them all to the user before editing anything:
  ```
  R10 mentoring -> Cyber Cohesion, description
    before: "...Shared in managing teams and supported the hiring of new engineers."
    after:  "...Shared in managing teams, mentoring developers, and supported the hiring of new engineers."
    evidence: what supports it (the user's code, an earlier confirmation), or "none found: confirm only if true"
  ```
- A proposal may only swap or insert the posting's keyword inside an existing sentence. New sentences, new or removed bullets, rewritten descriptions, dates, titles or companies are separate requests the user must approve explicitly.
- Apply only the proposals the user confirms, then rebuild, `--preview`, publish, and report the verdict.

**Never**
- Change the look of `template/resume.html`, `template/fonts/` or `template/assets/` without the user's explicit approval: no font, size, color, spacing, margin or other CSS edits, even to fit 3 pages. Fit content within the rules instead, or ask, showing the exact change proposed.
- Invent experience, or claim a skill, version or sub-feature the user hasn't used ("Vue 3" was true, "Vue 3 / Composition API" was not).
- Hide a regression: report the `--preview` verdict after every change, including when coverage drops because a false claim was removed.

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
