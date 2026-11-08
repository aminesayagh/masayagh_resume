---
name: publish-resume
description: Publish a job's tailored resume PDF to the portfolio site (masayagh.com) so the user can share or download it. Use after any rebuild of a job's PDF, when the user asks to send/upload/publish a resume to the portfolio or website, or asks for a resume link for a company.
---

# Publish a resume to the portfolio

One command sends a job's PDF to the portfolio site:

```bash
.venv/bin/python src/publish_resume.py jobs/<slug>/job.json
```

It prints the public link:

```
https://www.masayagh.com/resume/<company>/<pdf_name>
e.g. https://www.masayagh.com/resume/theodo/Mohamed-Amine-Sayagh-Software-Engineer-Fullstack-Theodo.pdf
```

The link ends in the PDF's real name, so a download keeps that name. Each publish **replaces** the previous PDF at the same link: there are no versions. A link already sent to a company always shows the latest resume.

## When to run it

- `src/new_job.py` publishes once, automatically, when it creates a job folder.
- **After every rebuild of a job's PDF** (`src/build_resume.py jobs/<slug>/content.json`), run the command above. The user expects the site to always have the latest version.
- If the PDF did not change, it prints "Already published, unchanged" and pushes nothing.

## What it does

1. Reads `company` and `pdf_name` from `jobs/<slug>/job.json` (both set by `new_job.py`; `company` must match `[a-z0-9-]+`).
2. Prepares its own clone of the portfolio repo at `/home/amine/projects/portfolio-publish` (cloned on first use) and resets it to `origin/main`.
3. Copies the PDF to `public/resume/<company>/<pdf_name>`, stages **only that file**, commits `Publish resume <company>/<pdf_name>`, runs `git pull --rebase`, and pushes to `main`.
4. Vercel deploys `main` to production in about a minute.

## Rules

- **Never commit in `/home/amine/projects/portfolio`.** It's the portfolio session's working copy, often on a feature branch with uncommitted work. Only the dedicated clone is used.
- Never `git add -A` in the clone: only the PDF path.
- Pushing to `main` is pre-approved by the user for resume PDFs. Anything else in the portfolio repo (`vercel.json`, pages, routes) belongs to the `portfolio` Claude session: message it with `SendMessage` (`to: "portfolio"`) instead of editing it.
- The job title is public in the link and file name. The user chose this.

## Checking it worked

About a minute after the push:

```bash
curl -sI https://www.masayagh.com/resume/<company>/<pdf_name> | grep -i -E "^HTTP|content-type|content-disposition|x-robots"
```

Expect `200`, `application/pdf`, `x-robots-tag: noindex, nofollow`, and **no** `content-disposition` (that header would override the download name). A 404 right after the push usually means the deploy is still running.

## Edge cases

- **Renamed `pdf_name`:** the old file stays on the site. Remove it in the clone (`git -C /home/amine/projects/portfolio-publish rm -- public/resume/<company>/<old>.pdf`, commit, `pull --rebase`, push).
- **Push rejected:** someone pushed in between. Rerun the command; it resets to the latest `origin/main` first.
- **A job folder made before this feature:** add `"company": "<slug>"` to its `job.json`.
