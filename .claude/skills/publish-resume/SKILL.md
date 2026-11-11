---
name: publish-resume
description: Publish a job's English resume and cover letter as configured in config.json (portfolio repo, folder, or nothing) so the user can share a link. Use after a job's PDF is rebuilt, when the user asks to publish/upload/send a resume to their portfolio or website, or asks for a resume link.
---

# Publish a resume

```bash
.venv/bin/python src/publish_resume.py jobs/<slug>
```

`src/tailor.py` already runs it after every build, so you rarely call it alone.

## What it does depends on `config.json` → `publish.mode`

| Mode | Effect |
|---|---|
| `none` (default; no `config.json`) | Nothing is published. Say so; the PDFs stay in `jobs/<slug>/`. |
| `folder` | Copies the resume and cover letter to `publish.folder`, at `publish.path`. |
| `git` | Commits them in a clone only the pipeline uses (`publish.clone`, default `<repo>-publish`), at `publish.path`, then pulls and pushes `publish.branch`. |

`config.example.json` documents every field. The public link of each file is `publish.url` (with `{site}`, `{company}`, `{version}`, `{file}`); it is printed and stored on the offer in `data/resume.db` (`resume_url`, `cover_letter_url`, `published_at`).

## Always true, in every mode
- Only the **English** resume and cover letter are published; the French version (`-FR`) stays local.
- A **sent** (frozen) job, a **not-ready** resume (`_` prefix) or a not-ready cover letter is never published.
- Version 2+ of a job goes under `v2/…`, so the link an employer received for an earlier version never changes.

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
