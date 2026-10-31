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

