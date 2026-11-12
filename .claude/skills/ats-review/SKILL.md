---
name: ats-review
description: Use the resume repo's ATS reviewer tools to check a resume, create a job file from a job posting, match a resume against a posting, or read and act on a review report. Use when the user mentions ATS, a job offer or posting, tailoring the resume, spelling or style of the resume, or checking the PDF.
---

# ATS reviewer

This repo builds tailored resume PDFs (`src/build_resume.py`) and reviews them against job postings. The reviewer is a **tailoring aid**: it shows what a posting asks for, what the PDF actually says, and what needs a human decision. It never predicts an employer's ATS score or a hiring outcome. Never describe its output as an "ATS score" or a "pass".

All commands run from the repo root with `.venv/bin/python`. Dependencies are in `requirements-review.txt` (`pypdf`, `pyspellchecker`). Every tool has `--help`.

## Files

Everything for one application lives together in one `jobs/` subfolder, named `<company>-<title>-v<N>` (e.g. `jobs/acme-backend-engineer-v1/`), laid out as `content/` (JSON content), `pdf/` (what is sent; `pdf/fr/` for French), `review/` (reports) and `history/` (copies kept when a sent job is reopened). The offer itself (posting, details, requirements) is in `data/resume.db`, read and written only through `src/offers.py`. `src/paths.py` is the only code that knows the folder layout.

| Path | What it is | Who edits it |
|---|---|---|
| `template/content/default.json`, `default-fr.json` | Master resume, **generated** from `data/resume.db` by `src/master.py` | Never edit; change the db with `src/master.py set …` (user's approval), which regenerates both |
| `template/layout/resume.html`, `template/layout/assets/`, `template/layout/fonts/` | Layout only | Don't change the design; parse fixes need the user's approval |
| `template/build/resume.pdf` | Baseline PDF built from `default.json` | `src/build_resume.py` |
| offer in `data/resume.db` (`src/offers.py`) | The posting, company, title, link, location and requirements (offers), and per folder its composition (pdf name, sent date); `offers.load(folder)` returns the job dict the review reads | Created by `new_job.py`, requirements parsed by `src/parse_offer.py`; checked by the user |
| `jobs/<slug>` | One posting as structured requirements | You draft it, the user reviews it |
| `jobs/<slug>/content/content.json` | Tailored resume content for this application, starts as a copy of `template/content/default.json` | The user, or you with approval |
| `jobs/<slug>/pdf/<pdf_name>` | Built PDF for this application, named by the offer's `pdf_name` (your name, job title, company) | `src/build_resume.py` |
| `template/layout/cover-letter.html` | Cover letter layout; the default letter is the newest approved `cover_paragraphs` row of each part in `data/resume.db` (`profile` cover_greeting/cover_closing, else plain ones); none yet means draft it | The user, or you with approval |
| `jobs/<slug>/content/cover.json` | This job's cover letter text, created from the default letter in `data/resume.db` on the first build | You, only when the user asks (`.claude/skills/draft-cover-letter/SKILL.md`) |
| `jobs/<slug>/<stem>-Cover-Letter.pdf`, `<stem>-Resume-and-Cover-Letter.pdf` | Cover letter alone, and resume + cover letter in one file; rebuilt with every resume build | `src/build_cover.py` (run it alone after editing `cover.json`) |
| `jobs/<slug>/review/review.json`, `review.md`, `interview.json` | Generated report and interview prep sheet | The tools only, never edited by hand |
| `jobs/<slug>/review/build.json` | The last build's warnings per part (`resume`, `cover`, `resume-fr`, `cover-fr`): why a PDF is not ready | The build scripts only |
| `spelling-allow.txt` | Words confirmed correct | Add a word only after the user confirms it, via `check_spelling.py --add` |
| `data/resume.db` (+ `data/resume.sql` in git) | Knowledge base: experiences and every approved line, cover paragraphs, skills with keywords (true synonyms) and years, offers, requirements, results of sent offers | Updated by the scripts (`src/db_sync.py` after every job build); add synonyms with `src/skills_inventory.py keyword`; no loose matches |

`src/new_job.py` scaffolds a new `jobs/<slug>/` folder interactively (company, job title, pasted posting). It **refuses to run** if `template/content/default.json` has any unresolved spelling/style/PDF-readability finding (warning or error) — fix the baseline first, so every new application starts clean. Run `src/check_template.py` on its own anytime to see that same list without starting a new application.

## Pipeline

Each tool defaults to its input's own folder: run against `template/content/default.json` for the baseline, or a `jobs/<slug>/` file for one application. Each step writes its report next to its input.

```bash
.venv/bin/python src/check_template.py                        # is template/ ready? lists findings, exit 1 if not
.venv/bin/python src/new_job.py --url JOB_URL                  # 0. scaffold jobs/<slug>/ from a link (blocks if template/ has findings)
.venv/bin/python src/new_job.py --company X --title Y --posting FILE   #    or from pasted text when the site blocks reading
.venv/bin/python src/check_spelling.py jobs/<slug>/content/content.json   # 1. spelling: warnings only
.venv/bin/python src/check_style.py jobs/<slug>/content/content.json      # 2. writing style: warnings only
.venv/bin/python src/build_resume.py jobs/<slug>/content/content.json     # 3. build jobs/<slug>/pdf/<pdf_name> + the two cover letter PDFs
.venv/bin/python src/check_pdf.py jobs/<slug>/pdf/<pdf_name>           # 4. PDF text: exit 1 on errors
.venv/bin/python src/check_job.py jobs/<slug>             # 5. validate the job file
.venv/bin/python src/review_ats.py --job jobs/<slug> --preview  # match per term, writes nothing, drafts OK
.venv/bin/python src/review_ats.py --job jobs/<slug>      # 6. full review, runs 1, 2, 4 and matching
.venv/bin/python src/publish_resume.py jobs/<slug>        # 7. publish as set in config.json (none/folder/git)
```

**From a link:** `src/fetch_posting.py URL` prints what it can read (title, company, location vs the user's, description) without creating anything. It reads schema.org JobPosting data, the Greenhouse API, schema.org microdata (SAP SuccessFactors), the Oracle Recruiting Cloud API, or the page rendered in Chrome. Works with LinkedIn, Greenhouse, Lever, careers.oracle.com and Capgemini; when a site blocks it, ask the user to paste the posting. `new_job.py --url` stores `url`, `location` and `location_match` in the offer (`data/resume.db`); tell the user the location verdict.

**After any edit to a job's `content.json`, run `src/tailor.py jobs/<slug>`:** it builds (which refreshes the review, interview prep and dashboard), publishes unless the PDF is over 3 pages or has errors, and prints the full table of everything not met. **Show that table to the user as printed, before any comment;** never summarize or drop rows.

**Years of experience per skill:** the `skills` table holds every resume skill, its keywords and the user's start date; years are computed to today. Each dashboard has a "Skills for application forms" box ready to paste. After adding skills to any `content.json`, run `src/skills_inventory.py sync`, then `missing`, and **ask the user for each start date** (never guess); record with `src/skills_inventory.py set "<skill>" YYYY-MM`.

**French version (local only):** when the posting is French and doesn't ask for English, the job needs a French version: `offers.language` = fr and `english_mentioned` = 0, both read from the posting. Every English build then runs `src/build_fr.py`: unchanged lines take their French from `template/content/default-fr.json`, tailored lines from `template/content/translations-fr.json`; anything new goes to `jobs/<slug>/content/translate-fr.json` for you to translate (concise, faithful, nothing added), then rerun. Output `<pdf_name stem>-FR.pdf` (+ French cover letter from `cover-fr.json`), same 3-page and `_` rules. Tailor and match in English only; the French version is never published. When `template/content/default.json` changes, update `default-fr.json` in step (same shape).

**Compose before tailoring, once:** once a job's requirements are drafted, run `src/compose.py jobs/<slug>`, then `src/tailor.py jobs/<slug>`. For every active activity of every experience it picks one approved line: the one with the most of the offer's terms (skill keywords count); on a tie the most recent. It writes the lines into `content.json` (text only), records in the db which library lines the composition uses (`offer_lines`) and prints each choice with its alternatives; show that list to the user. It runs **only once per job** (a composition that already has `offer_lines`): a composed job refuses, so approved edits are never replaced by newer library lines. After that, change only the lines agreed with the user. Summary, title and skills are per job in `content.json` and never touched by composition or by master edits.

**Activities:** lines that say the same thing in different words share an activity (`bloc_activities` table; `bloc_descriptions.activity_id`). The JSON is read as **text only**: lines are matched to the library by exact text (a resume never repeats a line). A new line approved later joins the activity of the line it replaced, which the db knows from the previous build (`offer_lines`); if that can't be told, it gets a new activity, inactive (`active = 0`) until the user reviews it, and it's reported. So the next composition can pick it. An inactive activity (`active = 0`) is never composed; only the user turns one on or off. A genuinely new activity needs the user's approval and a new `bloc_activities` row.

**Knowledge base:** before proposing experience edits, query the library for approved lines first: `SELECT json_extract(d.text, '$.en') FROM bloc_descriptions d JOIN description_skills ds ON ds.description_id = d.id JOIN skill_keywords k ON k.skill_id = ds.skill_id WHERE k.keyword = lower('<term>') AND d.status = 'approved'` (via `src/db.py`'s `connect()`). Reuse an approved line before writing a new one. Every build records new lines automatically.

**Sent = frozen:** when the user sends an application, run `src/offers.py sent jobs/<slug> [YYYY-MM-DD]` (default today); it records the date and snapshots the review's results. From then on `build_resume.py`, `build_cover.py`, `build_fr.py`, `tailor.py` and `publish_resume.py` refuse that folder, and `check_template.py` no longer lists it for refresh. Never edit a sent folder or propagate template changes into it; changes go into a new version folder. See AGENTS.md.

**Not ready = `_` prefix:** a job PDF over 3 pages or with a broken skills layout is saved as `_<pdf_name>` and the ready-named file is removed. `publish_resume.py` refuses it and the dashboard labels it "NOT READY, do not send". Never rename it by hand; fix the content and rebuild.

**Every job PDF build refreshes the review:** `src/build_resume.py jobs/<slug>/content/content.json` re-runs the review (no network), prints what changed since the previous report with a verdict, and saves `review.md`/`review.json` and `interview.json`, which the dashboard reads, so it is never older than the PDF. (Skipped for the template, for `-o` builds and before requirements exist.)

**While tailoring,** use `--preview` after each rebuild instead of ad-hoc scripts: it lists every term's status and the PDF line it matched, then compares with the saved `review.json` and ends with a verdict (`no regression`, or `REGRESSION:` with what got worse). Report that verdict to the user after each change; rerun without `--preview` to save the new baseline once they accept it. `build_resume.py` warns when the PDF goes over 3 pages and prints the start of the last page, so you know what spilled. Add confirmed spellings with `src/check_spelling.py --add WORD`, never by editing `spelling-allow.txt` by hand. After a template change, `src/check_template.py` lists job folders that are still untouched template copies (the offer's `template_sha`); those are safe to refresh with `cp template/content/default.json`, rebuild and publish.

**Dashboard:** run the local app with `python3 start.py` (builds the Vue front in `dashboard/web/` and serves it with FastAPI), then http://127.0.0.1:8000. It only reads the db and job folders; its open points are in `dashboard/notice.md`. Job pages are no longer written into `jobs/`; `dashboard/` is separate and only reads them. To change a sent job: `src/new_job.py --from jobs/<slug>` creates the next `-vN` folder: summary, title, skills and cover letters are copied, and the experience lines are composed again from the library (db -> json), so the new version gets the latest approved wording. The sent folder keeps its own `content.json` untouched. Publishing the new version replaces the previous one at the same link.

**Publishing (step 7):** run it after every rebuild of a job's PDF. Details and rules: [`../publish-resume/SKILL.md`](../publish-resume/SKILL.md).

`src/new_job.py` already runs 1, 2, 3 and a partial version of 6 (no matching yet, since the offer (`data/resume.db`) has empty `requirements`). To review a posting once requirements are drafted, step 6 is enough: it finds the PDF (the offer's `pdf_name`) and `content.json` next to the job file. Add `--no-network` when offline. Otherwise the tool opens every web link in the PDF (contact, projects, badges; redirects followed). `src/check_template.py` always does, so a broken link (HTTP 4xx/5xx) blocks `new_job.py`; being offline is only a note.

## Creating a job file from a posting

`src/new_job.py` creates the folder, parses the posting with `src/parse_offer.py` (one Haiku call through the `claude` CLI, cached in `data/cache/parse_offer/`), saves the offer and its requirements in `data/resume.db`, composes the experience lines, builds the resume and writes the review. Without the parser (no CLI or login), the job is created without requirements and says so.

**What is stored:** a requirement is only *the offer asks for this keyword*: `requirements` (offer, keyword, priority 100 must-have / 0 preferred, optional `min_years`) linked to `skill_keywords`. The parser gives each skill a type (technical, design, ai, soft, language, location, education; `none` items are skipped), a priority and `min_years`. No quote or line is stored.

**No duplicate skills (layer 1):** a skill is the concept, its keywords are every way of writing it. A posting's word is matched to an existing keyword first: same spelling once lowercased and ignoring spaces, hyphens and dots (`event-driven` = `event driven`, `node.js` = `nodejs`), and with or without a final s (`apis` = `api`). Only a word with no match creates a new skill, saved with `confirmed = 0`. **Layer 3:** the user reviews unconfirmed skills in the dashboard and merges a duplicate into the right skill (the merge UI is still to build); until then, add a synonym with `src/skills_inventory.py keyword "<skill>" "<word>"`. Never ask a model to decide synonyms (rejected by the user).

**Check what the parser saved** before tailoring: list the job's requirements (`src/review_ats.py --job jobs/<slug> --preview`) and tell the user about wrong types or priorities; fix them in the db, never by editing review files.

## Reading results

**PDF and content checks:** `error` blocks use (unreadable PDF, missing name or email, image-only page). `warning` is advice, because spelling and style can be correct even when flagged. `info` is context only.

**Job title:** the review warns when `content.json`'s `role` differs from the posting's title (from the offer's "Company — Title"). Tell the user, and propose the posting's title only if it truthfully describes them.

**Matching** gives two results per requirement. Report them separately:

- **Keyword:** `exact` means the posting's term is in the PDF, which recruiter search sees. `alias` means the wording differs, so suggest the posting's term. `absent` means the term is not in the PDF.
- **Evidence:**
  - `met`: found in experience, education, languages or header text.
  - `partial`: found only in the skills list or summary (a claim, not proof), or only some terms are met.
  - `missing`: no supporting text in this PDF. It does **not** mean the user lacks the skill.
  - `uncertain`: the text cannot support a decision.

**Years of experience:** reported two ways, with overlaps counted once and with every job added up. `met` needs the first number to reach the minimum.

**Evidence coverage** (v3) is Σ weight × (1 met, 0.5 partial, 0 otherwise) ÷ Σ weight, per priority, where the weight comes from the skill's type (`TYPE_WEIGHTS` in `src/review_ats.py`: hard skills 1, education and language 0.5, soft and location 0.25, not typed 0.5). The **overall** figure covers every requirement, with a preferred one weighted ¼ of a must-have (`PRIORITY_WEIGHTS`). Always present it with its formula, never as an ATS score, and never combined with PDF readability.

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
- The **number of skills shown stays the same** as in `template/content/default.json`, in total and per row. You may replace skills, never add extra ones.
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
- Change the look of `template/layout/resume.html`, `template/layout/fonts/` or `template/layout/assets/` without the user's explicit approval: no font, size, color, spacing, margin or other CSS edits, even to fit 3 pages. Fit content within the rules instead, or ask, showing the exact change proposed.
- Invent experience, or claim a skill, version or sub-feature the user hasn't used ("Vue 3" was true, "Vue 3 / Composition API" was not).
- Hide a regression: report the `--preview` verdict after every change, including when coverage drops because a false claim was removed.

## Rules

- **Never invent experience.** Suggestions say what the posting asks for and where the PDF stands. Only add a skill or term to a `content.json` when the user confirms it is true. "Missing" is information, not a gap to fill.
- **Don't edit a `review.json`/`review.md` (or any generated report) by hand.** When a result is wrong, add an override to the job file with `id`, `status`, `reason` and `pdf_quote` (the PDF text the decision relies on, or null). The report keeps the automated finding and flags the override as stale when that quote leaves the PDF. Prefer fixing the resume over overriding.
- **Don't weaken a check to make a report look better.** No loose aliases, no allowlisting words the user hasn't confirmed, and no downgrading errors.
- **`template/content/default.json` must stay clean.** `src/new_job.py` blocks creating a new job folder while the baseline has any spelling/style/PDF-readability finding (warning or error), because every new application starts from it. Fix the baseline before scaffolding; don't bypass the gate.
- **After editing content or the template,** rebuild the PDF before re-running `src/check_pdf.py` or `src/review_ats.py`. They read the PDF, not the JSON.
- **The user values reports as a record.** Summarize findings, but keep the full list available. Don't trim reports.
- **Tests:** `.venv/bin/python -m unittest discover -s tests -t .`. Run them after changing any tool.

## Known limits

- English spelling only.
- The style rules are text patterns, not judgement.
- Matching is literal plus the skill keywords in `data/resume.db`. There is no semantic or AI matching, so related wording is missed unless it's an alias.
- LinkedIn often refuses automated link checks, which is reported as "open it in a browser", not as broken.
- The section split depends on the template headings. If the headings change, `check_pdf.template_headings` picks them up from `template/layout/resume.html`.

## Requirement extraction: decision record (2026-11-11)

**Superseded 2026-11-12:** requirements now come from `src/parse_offer.py` (Haiku, typed skills with priority and min_years); `src/draft_job.py` and the `job-requirements` agent were removed. The record below explains the earlier choice.


Kept: `src/draft_job.py` + the Haiku `job-requirements` agent; skills linked by exact keyword. Benchmark on 6 jobs (191 lines, 226 terms): GLiNER2.5 83% of terms (weakest at telling requirements from company text), Qwen3.5 9B 86% but ~95 s per posting; `draft_job.py missed` catches what drafting misses. Fuzzy skill linking (multilingual-e5 + LLM check) ranked the right skill first 84% of the time but made confident mistakes (`Coaching` → `Harness Eng`) and adds dependencies.
- **Known gaps:** only 86 of 210 requirement terms link to a skill (exact keyword needed: `ES6` vs `ES6+`, `component library` vs `component libraries`; fix with `skills_inventory.py keyword`); skill types `soft`/`language` unused; no AI skill finer than "artificial intelligence".
- **Revisit when:** unlinked terms keep piling up (then build the e5 + LLM-verify linker, every link confirmed by the user), or 30–50 jobs have reviewed requirements (then train a classifier as a second opinion on line sections and priorities).

