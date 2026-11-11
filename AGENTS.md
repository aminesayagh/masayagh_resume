# Instructions for AI assistants

Before checking a resume, creating a job file from a posting, or reviewing a resume against a job, read and follow [`.claude/skills/ats-review/SKILL.md`](.claude/skills/ats-review/SKILL.md). It describes the tools, the order to run them, how to read their results, and the rules that matter most:

- Never invent experience.
- Correct wrong results with overrides in the job file, never by editing `analysis/`.
- Never present the output as an ATS score.
- **Never change a job folder whose files were sent** (`"sent": "YYYY-MM-DD"` on its offer): no edits to its content, cover letter, requirements or PDFs, no rebuild, no republish. The folder must keep exactly what the employer received. Template-wide changes (new summary, merged roles) apply to new jobs only; never propagate them into sent jobs. To change a sent application, create a new version folder. When the user says they sent or applied with a job, add `"sent"` with that date right away. The scripts refuse to rebuild, translate or publish a sent job; never remove `"sent"` to get around it. Only the user reopens a sent job (the dashboard's Reopen button, which first copies the sent files into `sent-<date>/`).

The knowledge base is `data/resume.db` (committed as `data/resume.sql`): reuse approved lines from it before writing new ones; the scripts keep it in sync with the job folders.

That file is the single source of these instructions; update it there, not here.

To write, tailor, translate or regenerate a job's cover letter, read and follow [`.claude/skills/draft-cover-letter/SKILL.md`](.claude/skills/draft-cover-letter/SKILL.md).
