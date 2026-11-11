---
name: publish-resume
description: Publish a job's English resume and cover letter as configured in config.json (portfolio repo, folder, or nothing) so the user can share a link. Use after a job's PDF is rebuilt, when the user asks to publish/upload/send a resume to their portfolio or website, or asks for a resume link.
---

# Publish a resume

```bash
.venv/bin/python src/publish_resume.py jobs/<slug>
```

`src/tailor.py` already runs it after every build, so you rarely call it alone.

This step only **sends the latest version to the portfolio** (repo or folder); the portfolio site is what publishes it. Tell the user "sent to the portfolio", not "published".

## What it does depends on `config.json` → `publish.mode`

| Mode | Effect |
|---|---|
| `none` (default; no `config.json`) | Nothing is published. Say so; the PDFs stay in `jobs/<slug>/`. |
| `folder` | Copies the PDF to `publish.folder`, at `publish.path`. |
| `git` | Commits it in a clone only the pipeline uses (`publish.clone`, default `<repo>-publish`), at `publish.path`, then pulls and pushes `publish.branch`. |

`config.example.json` documents every field. The public link is `publish.url` (with `{site}`, `{company}`, `{file}` = the resume's file name); it is printed and stored on the offer in `data/resume.db` (`resume_url`, `published_at`; `cover_letter_url` stays empty, the letter is inside the same PDF).

## Always true, in every mode
- **One PDF per application**, at the resume's link: the resume with its cover letter in the same file (`…-Resume-and-Cover-Letter.pdf`) when the letter is ready, otherwise the resume alone. The cover letter is never sent as a separate file.
- Only the **English** version is published; the French version (`-FR`) stays local.
- A **sent** (frozen) job or a **not-ready** resume (`_` prefix) is never published. A not-ready cover letter only means the resume goes alone.
- An application has **one public link**: a new version (`-v2`, …) publishes to the same place, replacing the previous one, so every employer's link serves the latest version.

## Rules for `git` mode
- **Never commit in `publish.repo` itself**; it may be the user's working copy with other work. Only the dedicated clone is used.
- Never `git add -A` in the clone; only the published files are staged.
- Choosing `mode: git` is the user's approval for pushing resume PDFs. Any other change to their site (pages, routes, config) is not part of this pipeline: ask the user.

## Checking a published link
About a minute after a push (if the site deploys from the branch):

```bash
curl -sI <printed link> | grep -i -E "^HTTP|content-type|content-disposition"
```

Expect `200` and `application/pdf`. A `content-disposition` header would override the download name. A 404 right after a push usually means the deploy is still running.

## Edge cases
- **Renamed `pdf_name`:** the old file stays published. Remove it in the clone or folder by hand if wanted.
- **Push rejected:** someone pushed in between. Rerun; it resets the clone to the latest remote branch first.
- **A job without `"company"` in the offer (`data/resume.db`):** add `"company": "<slug>"` ([a-z0-9-]+).
