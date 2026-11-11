# Job dashboard (local)

Browse, search and act on the job folders in `jobs/`. It runs on your machine only.

```bash
.venv/bin/python -m uvicorn dashboard.app:app --host 127.0.0.1 --port 8000
# then open http://127.0.0.1:8000
```

Install once: `VIRTUAL_ENV=$PWD/.venv uv pip install -r dashboard/requirements.txt`.

| Page | What |
|---|---|
| `/` | All jobs: status (ready, draft, not ready, sent), coverage, location, French version. Search company, title or posting text; filter by status, skill asked, location. |
| `/job/<slug>` | One job: files (EN/FR resume, cover letter, combined), requirements and gaps, interview prep, skills with years, posting. Actions. |
| `/skills` | Every posting term across jobs, how many jobs ask for it, and per job the best result on that job's resume. |

**Actions** (each asks for confirmation): Mark as sent (freezes the job), Tailor (`src/tailor.py`), Build French version (`src/build_fr.py`), New version from this job (`src/new_job.py --from`).

The app reads `jobs/` and never writes there itself: every action runs the `src/` scripts, so their rules hold (sent jobs are frozen, `_` = not ready, 3 pages). The one direct write is "Mark as sent", which adds `"sent"` to `job.json`. Steps that need judgement (drafting requirements, proposing edits, writing cover letters) are not in the app.
