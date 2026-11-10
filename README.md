# Tailored Resume

Generate a job-specific A4 resume PDF from a JSON content file, and review it against a job posting. The HTML template handles layout, page breaks, fonts, and a portfolio QR code.

[View the default PDF](template/resume.pdf)

## Requirements

- Python 3.10 or newer
- Google Chrome available as `google-chrome` in WSL or Linux

Create a local environment and install the Python dependency:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The QR generator is bundled in `src/vendor/`, so it needs no additional install.

## Layout

- `template/` — the master resume: `default.json` (content), `resume.html` (layout), `resume.pdf` (baseline build).
- `jobs/<company>-<title>-v<N>/` — one folder per application: `posting.txt`, `job.json` (requirements), `content.json` (tailored content, starts as a copy of `template/default.json`), the PDF (named `<Your-Name>-<Job-Title>-<Company>.pdf`, set by `pdf_name` in `job.json`), and the generated `review.json`/`review.md`.
- `src/` — all the tools.

## Start a new job application

```bash
.venv/bin/python src/new_job.py --url <job posting link>      # reads title, company, posting, location
.venv/bin/python src/new_job.py                               # or paste the posting
```

`--url` reads the posting with `src/fetch_posting.py` (works with LinkedIn, Greenhouse, Lever, Teamtailor, Oracle careers, SAP SuccessFactors; try `src/fetch_posting.py <link>` alone to preview) and compares the job's location with yours. Without it, the script prompts for the company, the job title, and the posting text (paste it, then press Ctrl-D).

Version 1 workflow after the folder exists:

1. **Draft requirements** with the `job-requirements` agent (`.claude/agents/job-requirements.md`, Haiku). It uses `src/draft_job.py` (`lines`, `apply`, `missed`): quotes are copied from line numbers, terms must be short, the location and degree lines must be covered, and every technology-looking word is covered or skipped with a reason.
2. **Review** with `src/review_ats.py --job jobs/<slug>/job.json`: report, `interview.json` (prep topics) and `dashboard.html` (one page per job), labelled draft until requirements are reviewed. `--preview` prints the match and compares with the last saved report (verdict: no regression / REGRESSION).
3. **Tailor** `content.json` within the rules in `.claude/skills/ats-review/SKILL.md` (3 pages, 6 skill rows of 4, experience edits proposed and confirmed first), rebuild, publish. It refuses to run if `template/default.json` has any unresolved spelling/style/PDF-readability finding — fix the baseline first, since every new application starts from it. On success it creates `jobs/<slug>/`, builds the resume, and writes a partial report (no job-matching yet). See [`docs/job-file-guide.md`](docs/job-file-guide.md) for drafting `job.json`'s requirements next.

To check whether the baseline is ready without starting a new application:

```bash
.venv/bin/python src/check_template.py
```

Rebuilds `template/resume.pdf` and lists every spelling/style/PDF-readability finding (same checks `new_job.py` gates on). Prints "ready" and exits 0 if there are none.

## Publish a resume to the portfolio

```bash
.venv/bin/python src/publish_resume.py jobs/company-role-v1/job.json
```

Pushes the job's PDF to the portfolio repo's `main` branch (from a dedicated clone at `/home/amine/projects/portfolio-publish`). It goes live at `https://www.masayagh.com/resume/<company>/<pdf_name>`, so a download keeps the PDF's real name. Each publish replaces the previous PDF at that link. `new_job.py` publishes automatically; rerun this after every rebuild of a job's PDF.

## Build a resume

Build the baseline version:

```bash
.venv/bin/python src/build_resume.py
```

Build one application's tailored version:

```bash
.venv/bin/python src/build_resume.py jobs/company-role-v1/content.json
```

The PDF is saved next to the JSON file: in a job folder it uses `job.json`'s `pdf_name`, otherwise `resume.pdf`. Use `-o path/to/resume.pdf` to choose another location. HTML is created temporarily during rendering and removed afterward.

## Edit content

The master resume content is `template/default.json`; each job folder's `content.json` starts as a copy of it. Keep the template unchanged. Add, remove, or reorder entries in the `experience`, `education`, `skills`, and `languages` lists. The layout adds pages as needed. Long experiences continue between complete bullet points, with the heading and description kept together. The build stops with a fit error if content cannot fit.

In `contact`, `website` is the displayed text and `website_link` is the clickable URL in the header, footer, and QR code. `email` sets both the displayed address and its email link. Change these fields in each job's `content.json`. To give the QR a separate destination, add `qr_url` to that file.

## Check spelling

Run this before building. `src/check_spelling.py` reads a content JSON and lists every word the English dictionary does not know, with suggested fixes and the field to edit (for example `experience[2].bullets[1]`). Each result is a **warning**, not an error, because product names and tech terms are often correct even when the dictionary does not know them. Company names, skills, institutions and locations are trusted automatically. Add other words you have confirmed to `src/spelling-allow.txt`.

```bash
.venv/bin/pip install -r requirements-review.txt
.venv/bin/python src/check_spelling.py                              # template/default.json
.venv/bin/python src/check_spelling.py jobs/company-role-v1/content.json
```

The report is saved to `spelling.json` next to the content file.

## Check writing style

`src/check_style.py` reads a content JSON and gives rule-based advice for the recruiter who reads the resume after the ATS: first person ("I", "my"), weak openers ("Helped", "Contributed to"), bullets over 30 words, a summary over 60 words, how many lines include a number or measurable result, and verbs repeated at the start of 3 or more lines. Everything is a warning or info, never an error.

```bash
.venv/bin/python src/check_style.py                                 # template/default.json
```

The report is saved to `style.json` next to the content file.

## Check the PDF text

Applicant tracking systems (ATS) read your resume by extracting the PDF's text. `src/check_pdf.py` extracts that text the same way and compares it with the content JSON next to it. It flags:

- **Readability:** image-only pages, missing fields, headings and dates broken across lines, non-standard section names, jobs without a title, and job headers repeated on a continuation page.
- **Contact and links:** email and phone format (including a country code), LinkedIn/GitHub/website addresses that exist only as icons and not as text, and links that do not open. Add `--no-network` to skip opening the links.
- **Dates:** single dates instead of ranges, reversed or future dates, overlapping jobs, and your years of experience counted two ways (overlaps once, and every job added up, as some parsers do).
- **File:** PDF title and author metadata, and a file name without your name in it.

```bash
.venv/bin/python src/check_pdf.py                       # template/resume.pdf + template/default.json
.venv/bin/python src/check_pdf.py jobs/company-role-v1/resume.pdf
.venv/bin/python -m unittest discover -s tests -t .  # self-test
```

The JSON report is saved to `pdf-check.json` next to the PDF. The command exits with code 1 on errors; warnings are advice. It checks text extraction only and is not a score from any employer's ATS. Later milestones (job requirements and evidence matching) are described in the [ATS reviewer plan](docs/ats-reviewer-plan.md).

## Describe a job posting

A job file (`jobs/<slug>/job.json`) lists what a posting asks for. Each requirement has the exact quote from the posting, a `must_have` or `preferred` priority, and the search terms in the posting's own wording. You mark each requirement as reviewed after checking it yourself. `src/check_job.py` validates the file: every quote must appear word for word in the posting, terms must come from the quote, nice-to-have lines cannot be marked `must_have`, and unreviewed requirements fail. See the [job file guide](docs/job-file-guide.md) and the [fictional example](jobs/fictional-full-stack-v1/job.json).

```bash
.venv/bin/python src/check_job.py jobs/fictional-full-stack-v1/job.json
.venv/bin/python src/check_job.py jobs/company-role-v1/job.json --draft   # while still reviewing
```

## Review a resume for a job (one command)

`src/review_ats.py` runs all the checks for one posting and writes a readable report:

```bash
.venv/bin/python src/review_ats.py --job jobs/fictional-full-stack-v1/job.json
.venv/bin/python src/review_ats.py --job jobs/company-role-v1/job.json
```

The report, `review.md` next to the job file (with `review.json` beside it), contains these sections in order:

1. **Decisions for you:** must-haves that are not met, stale overrides, and PDF errors.
2. **PDF readability:** the `src/check_pdf.py` findings.
3. **Content checks:** spelling and style warnings.
4. **Must-have requirements, then preferred requirements:** gaps first, each with the posting quote, your PDF quote and page, the reason, and a rule-based suggestion such as "the posting says X; your PDF says Y".
5. **Summary:** the met/partial/missing/uncertain counts, and **evidence coverage**: (met + 0.5 × partial) ÷ requirements, per priority. Evidence coverage is not an ATS score or a hiring probability, and it is kept separate from PDF readability.

Without `--cv`/`--content`, the command uses `resume.pdf` and `content.json` next to the job file. To correct a result, add an override to the job file (see the [job file guide](docs/job-file-guide.md#overriding-a-result)).

## Match your resume to a job

`src/match_job.py` checks a validated job file against the resume PDF text. For each requirement it reports two separate things:

- **Keyword:** whether the posting's exact term appears anywhere in the PDF, which is what a recruiter's search sees. The result is `exact`, `alias` (wording differs: use the posting's term), or `absent`.
- **Evidence:** whether the resume backs the requirement up. `met` means it was found in experience, education, languages or header text. `partial` means it was found only in the skills list or summary (a claim, not proof), or only some of the requirement's terms were met. `missing` means there is no supporting text in this PDF; it does not mean you lack the skill. `uncertain` means the text cannot support a decision.

Every `met` or `partial` result quotes the exact PDF line and its page. "At least N years" requirements are computed from your job dates. Matching is deterministic: no model and no network. Alternative spellings that count as the same term (for example Postgres for PostgreSQL) are in `src/aliases.json`; keep only true synonyms there.

```bash
.venv/bin/python src/match_job.py jobs/fictional-full-stack-v1/job.json
.venv/bin/python src/match_job.py jobs/company-role-v1/job.json
```

The report is saved to `match.json` next to the job file.

## For AI assistants

The ATS reviewer's usage rules for AI tools are in [`.claude/skills/ats-review/SKILL.md`](.claude/skills/ats-review/SKILL.md). Claude Code loads that file automatically as a skill. Other tools reach it through [`AGENTS.md`](AGENTS.md).

## Optional: local cv-matcher example

The [fictional job offer](jobs/fictional-full-stack-v1/posting.txt) and [example result](jobs/fictional-full-stack-v1/cv-matcher-example.json) show a local, model-assisted resume match using [cv-matcher](https://github.com/officialgabzz/cv-matcher). This is an illustrative score for an invented role, not a score from an employer's ATS.

Use Python 3.12 for the local-model environment. With `uv`, install the optional dependencies:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-ats.txt
```

Then run:

```bash
.venv/bin/python examples/score_cv_matcher.py
```

The first run downloads [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) to `.hf-cache/` (roughly 3 GB). A CUDA GPU is recommended; no API key is required. The runner uses `cv-matcher` to extract the full PDF text and validate its result. It requests four category ratings from the local model, computes the weighted total (35% skills, 30% experience, 20% education, 15% keywords), and checks skill terms literally in the PDF and posting. It refuses the library's silent rule-based fallback.

For another posting, pass `--cv`, `--job`, `--out`, and a comma-separated `--skills` list. The score is a model judgment and may vary with the model or job wording; review the evidence before editing your resume.

## Project files

| Path | Purpose |
| --- | --- |
| `template/default.json` | Master resume content |
| `template/resume.html`, `template/fonts/`, `template/assets/` | Page layout, print styles, bundled Poppins fonts (OFL license) and SVG logos |
| `template/resume.pdf` | Baseline build |
| `jobs/<slug>/` | One folder per application: posting, job requirements, tailored content, built PDF, and report |
| `src/build_resume.py` | Validates content, creates the QR, checks page fit, and exports the PDF |
| `src/new_job.py` | Scaffolds a new `jobs/<slug>/` folder from a pasted posting |
| `src/check_template.py` | Checks whether `template/` is ready (no spelling/style/PDF findings) to start a new application |
| `src/check_spelling.py`, `check_style.py`, `check_pdf.py`, `check_job.py`, `match_job.py`, `review_ats.py` | ATS reviewer tools |
| `src/aliases.json`, `src/spelling-allow.txt` | Reviewer word lists: true synonyms and confirmed spellings |
| `src/vendor/` | Bundled QR generator and its license |
| `tests/` | Tests for the reviewer (`.venv/bin/python -m unittest discover -s tests -t .`) |
| `docs/` | Reviewer plan and job file guide |
| `examples/` | Local cv-matcher runner (unrelated experiment, see `docs/ats-reviewer-plan.md`) |
| `.claude/skills/ats-review/`, `AGENTS.md` | Instructions for AI assistants |

