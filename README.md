# Tailored Resume

Generate a job-specific A4 resume PDF from a JSON content file. The HTML template handles layout, page breaks, fonts, and a portfolio QR code. The only saved build output is a PDF.

[View the default PDF](output/default.pdf)

## Requirements

- Python 3.10 or newer
- Google Chrome available as `google-chrome` in WSL or Linux

Create a local environment and install the Python dependency:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The QR generator is bundled in `vendor/`, so it needs no additional install.

## Build a resume

Build the default version:

```bash
.venv/bin/python build_resume.py
```

Create a version for a job offer:

```bash
cp content/default.json content/company-role.json
# Edit content/company-role.json
.venv/bin/python build_resume.py content/company-role.json
```

The PDF is saved as `output/<JSON filename>.pdf`. Use `-o path/to/resume.pdf` to choose another location. HTML is created temporarily during rendering and removed afterward.

## Edit content

All resume content is in `content/default.json`. Copy it before tailoring a resume; keep the template unchanged. Add, remove, or reorder entries in the `experience`, `education`, `skills`, and `languages` lists. The layout adds pages as needed. Long experiences continue between complete bullet points, with the heading and description kept together. The build stops with a fit error if content cannot fit.

In `contact`, `website` is the displayed text and `website_link` is the clickable URL in the header, footer, and QR code. `email` sets both the displayed address and its email link. Change these fields in each job-specific JSON file. To give the QR a separate destination, add `qr_url` to that file.

## Check spelling

Run this before building. `check_spelling.py` reads your content JSON and lists every word the English dictionary does not know, with suggested fixes and the field to edit (for example `experience[2].bullets[1]`). Each result is a **warning**, not an error, because product names and tech terms are often correct even when the dictionary does not know them. Company names, skills, institutions and locations are trusted automatically. Add other words you have confirmed to `spelling-allow.txt`.

```bash
.venv/bin/pip install -r requirements-review.txt
.venv/bin/python check_spelling.py                       # content/default.json
.venv/bin/python check_spelling.py content/company-role.json
```

The report is saved to `analysis/<content name>.spelling.json`.

## Check writing style

`check_style.py` reads the content JSON and gives rule-based advice for the recruiter who reads the resume after the ATS: first person ("I", "my"), weak openers ("Helped", "Contributed to"), bullets over 30 words, a summary over 60 words, how many lines include a number or measurable result, and verbs repeated at the start of 3 or more lines. Everything is a warning or info, never an error.

```bash
.venv/bin/python check_style.py                          # content/default.json
```

The report is saved to `analysis/<content name>.style.json`.

## Check the PDF text

Applicant tracking systems (ATS) read your resume by extracting the PDF's text. `check_pdf.py` extracts that text the same way and compares it with your content JSON. It flags:

- **Readability:** image-only pages, missing fields, headings and dates broken across lines, non-standard section names, jobs without a title, and job headers repeated on a continuation page.
- **Contact and links:** email and phone format (including a country code), LinkedIn/GitHub/website addresses that exist only as icons and not as text, and links that do not open. Add `--no-network` to skip opening the links.
- **Dates:** single dates instead of ranges, reversed or future dates, overlapping jobs, and your years of experience counted two ways (overlaps once, and every job added up, as some parsers do).
- **File:** PDF title and author metadata, and a file name without your name in it.

```bash
.venv/bin/python check_pdf.py                       # output/default.pdf + content/default.json
.venv/bin/python check_pdf.py output/company-role.pdf
.venv/bin/python -m unittest test_check_pdf test_check_spelling test_check_style  # self-test
```

The JSON report is saved to `analysis/<pdf name>.pdf-check.json`. The command exits with code 1 on errors; warnings are advice. It checks text extraction only and is not a score from any employer's ATS. Later milestones (job requirements and evidence matching) are described in the [ATS reviewer plan](docs/ats-reviewer-plan.md).

## Optional: local cv-matcher example

The [fictional job offer](examples/fictional_full_stack_job.txt) and [example result](analysis/fictional_full_stack.json) show a local, model-assisted resume match using [cv-matcher](https://github.com/officialgabzz/cv-matcher). This is an illustrative score for an invented role, not a score from an employer's ATS.

Use Python 3.12 for the local-model environment. With `uv`, install the optional dependencies:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-ats.txt
```

Then run:

```bash
.venv/bin/python examples/score_cv_matcher.py
```

The first run downloads [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) to `.hf-cache/` (roughly 3 GB). A CUDA GPU is recommended; no API key is required. The runner uses `cv-matcher` to extract the full PDF text and validate its result. It requests four category ratings from the local model, computes the weighted total (35% skills, 30% experience, 20% education, 15% keywords), and checks skill terms literally in the PDF and posting. It refuses the library's silent rule-based fallback. The result is written to `analysis/`, keeping `output/` PDF-only.

For another posting, pass `--cv`, `--job`, `--out`, and a comma-separated `--skills` list. The score is a model judgment and may vary with the model or job wording; review the evidence before editing your resume.

## Project files

| Path | Purpose |
| --- | --- |
| `build_resume.py` | Validates content, creates the QR, checks page fit, and exports the PDF |
| `content/default.json` | Master content for new job-specific copies |
| `template/resume.html` | Page layout and print styles |
| `template/fonts/` | Bundled Poppins fonts and their OFL license |
| `template/assets/` | Local SVG logos used during PDF rendering |
| `vendor/` | Bundled QR generator and its license |
| `output/default.pdf` | Default sample PDF |
| `examples/` | Local cv-matcher runner and fictional job offer |
| `analysis/` | Example assessment JSON |

