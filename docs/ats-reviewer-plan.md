# ATS reviewer implementation plan

## Goal

For each job posting, produce a review of the **generated PDF** that shows what the posting asks for, what the PDF actually says, and what needs a human decision. The result is a resume tailoring aid, not a prediction of an employer's ATS score.

The current `examples/score_cv_matcher.py` remains an optional experiment. Its model-generated percentage is not the acceptance criterion for the new reviewer.

> **Layout note:** the tools now live in `ats/` (reviewer), `builder/` (PDF build, template, vendor) and `tests/`. File names below are unchanged; prefix them with those folders.

## Working contract

- Resume source stays in `content/<job-slug>.json`; `template/` stays presentation-only; `output/` contains PDFs only.
- A reviewed posting lives in `jobs/<job-slug>.json`. It contains the original posting text or a local text-file reference, plus structured requirements. Each requirement has a stable ID, source quote, `must_have` or `preferred` priority, and a short description. Any requirement without a clear source quote is flagged for human review.
- A run writes `analysis/<job-slug>.json` and a readable `analysis/<job-slug>.md`. Reports contain no unsupported “ATS pass” claim.
- Every `met` or `partial` result must cite an exact quote from extracted PDF text and its page number. `missing` means no supporting evidence was found in this PDF; `uncertain` means the available text cannot support a confident decision. Neither status asserts that the candidate lacks the skill.
- A reviewer can override an assessment with a reason; the original automated finding remains visible.

## Milestone 0 — Spelling

**Build:** Spell-check the content JSON before the PDF is built. Report each unknown word as a warning with suggestions and the field path, never as an error, because names and tech terms are often correct. Trust words from names, companies, skills, institutions and locations. Confirmed words go in `spelling-allow.txt`.

**Status:** done — `check_spelling.py` (`pyspellchecker`, English, offline), `test_check_spelling.py`, report in `analysis/<content>.spelling.json`.

## Milestone 1 — PDF text and integrity checks

**Build:** Add a PDF reader that extracts text page by page and checks that the generated document is readable. Compare important fields from `content/<job-slug>.json` with the extracted text: name, contact address, experience headings and dates, education, and section headings. Flag missing, duplicated, or badly ordered text. Keep layout and rendering checks separate from job fit.

Also check what parsers commonly trip on: section headings that are not standard names (Summary, Skills, Experience, Education, Languages), headings or date ranges broken across lines, an entry header repeated on a continuation page, entries without a job title, and lines repeated on every page (footers).

Also check contact data (email and phone format, LinkedIn/GitHub/website written as text and not only as icons, links that open), dates (ranges, order, future dates, overlaps, years of experience counted with overlaps once and summed), and file metadata (PDF title and author, file name). Separately, `check_style.py` gives rule-based writing advice on the content JSON (first person, weak openers, long bullets, measurable results, repeated verbs) as warnings only.

**Status:** done — `check_pdf.py` (single file; split into a package only when it outgrows one), `test_check_pdf.py`, report in `analysis/<pdf>.pdf-check.json`.

**Deliverables:** `check_pdf.py`, a machine-readable check result, and a CLI command that works on `output/default.pdf`.

**Done when:** The default PDF extracts with page numbers and all critical fields are found; a deliberately broken or image-only PDF produces an actionable warning; a check never declares compatibility with a specific employer's ATS.

## Milestone 2 — Job requirement contract

**Build:** Define and validate the `jobs/*.json` schema. Convert `examples/fictional_full_stack_job.txt` into the first structured fixture. Validate source quotes automatically: each quote must appear verbatim (after whitespace normalization) in the posting text. A model may suggest requirements from the start, since a human still confirms the `must_have`/`preferred` priority before scoring. Support a computed requirement type for years of experience, reusing `check_pdf.check_dates` (it already reports `experience_years`), because no quote can prove it. Keep responsibilities, explicit requirements, preferred qualifications, location/work authorization, and screening questions distinguishable. Do not infer a hard gate from vague language.

**Status:** done — `check_job.py` (validator), `jobs/fictional_full_stack.json` (18 requirements: 9 must-have, 9 preferred), `docs/job-file-guide.md`, `test_check_job.py`. Requirements carry `terms` in the posting's exact wording for milestone 3's keyword check. Model suggestion of requirements is not built yet; files are written by hand and the validator catches mistakes.

**Deliverables:** `jobs/fictional_full_stack.json`, schema validation, and a short guide for creating a job file from a posting.

**Done when:** Every scored requirement traces to text in the posting; malformed or unreviewed requirements fail validation; the fictional posting can be reviewed without a model download.

## Milestone 3 — Evidence assessment

**Build:** Match each reviewed requirement to page-level PDF excerpts. Start with deterministic normalization and a small, explicit alias list (for example, `React / Next.js`). Use semantic/model matching only to propose candidates for verification. Record one of `met`, `partial`, `missing`, or `uncertain`, plus quote, page, method, and short rationale. Report two things per requirement: **keyword present** (the posting's exact term appears anywhere, including the skills list, which is what recruiter search sees) and **evidence** (experience text supports it). A bare keyword in the skills list should not satisfy evidence for professional experience. A match found only through an alias is reported as "wording differs" with the posting's term, since ATS keyword search is mostly literal.

**Status:** done — `match_job.py`, `aliases.json`, `test_match_job.py`, report in `analysis/<job>.match.json` (rules `version` 1). The PDF text is split into sections (header, summary, skills, experience, education, languages, footer) using the template headings. Evidence = experience, education, languages or header; claim only (`partial`) = skills or summary. A multi-term requirement is `met` only when all its terms are met. Years requirements are `met` when the merged years reach the minimum, and `partial` when only the summed years do. Semantic/model matching is not built; the alias list covers wording variants.

**Deliverables:** `ats_review/evidence.py` and a per-requirement result in the JSON report.

**Done when:** Every positive result has a verifiable PDF quote; ambiguous experience requirements become `partial` or `uncertain`; repeated runs with the same inputs produce the same result; no model-generated claim can enter the report without evidence verification.

## Milestone 4 — Decision report and CLI

**Build:** Add `review_ats.py` with `--cv`, `--job`, `--content`, and `--out` options. Show PDF check findings first, then must-have requirements, then preferred requirements. Edit suggestions are rule-based only (for example "posting says X, PDF says Y"); no model-written suggestion enters the report. Support a reasoned human override in the job review file while preserving the automated finding. Each override stores the PDF quote it was made against, and is flagged stale when that quote is no longer in the PDF. Show counts for `met`/`partial`/`missing`/`uncertain` separately. If a numeric summary is useful, label it **evidence coverage**, publish its fixed formula and version, and never use it as a hiring probability or universal ATS score. Do not combine parseability and job coverage into one number.

**Status:** done — `review_ats.py`, `test_review_ats.py`, reports `analysis/<job>.review.md` and `.review.json`. The report opens with a "Decisions for you" section (must-haves not met, stale overrides, PDF errors). Overrides live in the job file under `overrides` (`id`, `status`, `reason`, `pdf_quote`) and are validated by `check_job.py`. Evidence coverage v1 = (met + 0.5 × partial) ÷ requirements, per priority.

**Deliverables:** JSON and Markdown reports under `analysis/`, documented command in `README.md`.

**Done when:** One command reviews the fictional posting against `output/default.pdf`; each report links findings to posting and PDF quotes; the report clearly identifies human decisions; `output/` remains PDF-only.

## Milestone 5 — Validate on real postings

**Build:** Collect 3–5 real postings relevant to the job search. For each, manually label the requirements and supporting resume excerpts before looking at the reviewer result. Include cases with missing skills, equivalent wording, a requirement only in a skills list, and a broken PDF. Compare disagreements and fix the rule or report wording before using the tool for applications.

**Deliverables:** Redacted evaluation fixtures where sharing is permitted, an error log, and a short evaluation summary in `analysis/` or `docs/`.

**Done when:** Every reported positive finding is traceable to a real PDF excerpt; must-have priorities match the posting's wording after human review; known broken PDFs are flagged; remaining disagreements are documented. Do not claim a benchmark accuracy or ATS pass rate from this small set.

## First implementation slice

Milestone 1 is shipped on its own: it needs no job file and already finds real issues in `output/default.pdf`. Fix those in `template/resume.html` next, then build milestone 2. The reviewer's dependencies live in `requirements-review.txt` (`pypdf` and `pyspellchecker`), separate from the model stack in `requirements-ats.txt`. The first real posting is needed at milestone 5; its text or URL can be supplied then.

## References

- [Greenhouse: reasons a resume parse can fail](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse)
- [LinkedIn Hiring Pro FAQ: qualifications and evidence](https://www.linkedin.com/help/linkedin/answer/a7463744)
