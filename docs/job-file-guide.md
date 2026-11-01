# Creating a job file

A job file turns a posting into a list of requirements the reviewer can check your resume against. Each requirement quotes the posting word for word, so every later finding traces back to what the employer actually wrote. Example: [`jobs/fictional_full_stack.json`](../jobs/fictional_full_stack.json).

## Steps

1. Save the posting text as `jobs/<job-slug>.txt` (copy it from the job page). You can also paste it into the job file as `posting_text`.
2. Create `jobs/<job-slug>.json` using the skeleton below. Use the same slug as your tailored content file, `content/<job-slug>.json`.
3. Add one requirement per thing the posting asks for. When one line lists several skills ("Experience with React, Python, SQL"), make one requirement per skill. They can all share the same quote.
4. Validate while you work: `.venv/bin/python ats/check_job.py jobs/<job-slug>.json --draft`
5. Re-read each requirement against the posting, set `"reviewed": true`, and validate again without `--draft`. The file can be used for scoring only when it shows 0 errors.

## Skeleton

```json
{
  "title": "Company — Role",
  "posting_file": "jobs/<job-slug>.txt",
  "requirements": [
    {
      "id": "R01",
      "section": "requirement",
      "priority": "must_have",
      "quote": "Experience with React, Python, SQL, API integration, and automated testing.",
      "description": "Professional experience with React",
      "terms": ["React"],
      "reviewed": false
    }
  ]
}
```

## Fields

| Field | Rule |
|---|---|
| `id` | Unique and stable (`R01`, `R02`…). Don't renumber after scoring starts, because overrides refer to these ids. |
| `section` | Where the line appears in the posting: `responsibility`, `requirement`, `preferred` (nice to have), `location` (location or work authorization), or `screening` (an application question). |
| `priority` | `must_have` or `preferred`. Use `must_have` only when the posting says so ("Requirements", "must", "at least"). Anything under "nice to have", or worded "a plus", "ideally" or "preferred", is `preferred`, and the validator rejects it as `must_have`. Responsibilities describe the work rather than set a gate, so they are usually `preferred`. |
| `quote` | Copied word for word from the posting. Spacing and line breaks may differ; the words may not. |
| `description` | A short plain-language summary. |
| `terms` | The words a recruiter would search for, in the **posting's exact wording** ("PostgreSQL", not "Postgres"). Each term must appear in the quote. |
| `kind` | `evidence` (default) for requirements found in your resume text. Use `years_experience` with `min_years` for "at least N years", which is computed from your job dates. |
| `note` | Optional. Your reasoning for anything ambiguous. |
| `reviewed` | Set to `true` only after you have checked the quote and the priority yourself. |

## Tips

- Leave out vague lines ("fast-paced environment", "team player") unless the posting makes them a stated requirement.
- Work-authorization and location lines are real gates for many ATS knockout questions. Record them as `location` even though no resume keyword proves them.
- When a requirement is ambiguous, prefer `preferred` and explain why in `note`. The reviewer reports `must_have` items first, so over-marking hides what matters.

## Overriding a result

When the automated result is wrong, add an override to the job file instead of editing the report. The automated finding stays visible next to your decision.

```json
"overrides": [
  {
    "id": "R07",
    "status": "met",
    "reason": "React is the main front-end stack at Phoenix AI",
    "pdf_quote": "Built and refined the front-end experience in close collaboration"
  }
]
```

- `status`: `met`, `partial`, `missing` or `uncertain`.
- `reason`: required. Explain why the automated result is wrong.
- `pdf_quote`: the PDF text your decision relies on, or `null` if it does not rely on any. When that text disappears from the PDF (for example after you edit the resume), the report marks the override as **stale** so you check it again.

Prefer fixing the resume over overriding: an override changes your report, not what an ATS or a recruiter reads.
