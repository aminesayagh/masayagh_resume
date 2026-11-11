# Dashboard: open points to work on later

Found while rebuilding the dashboard from `dashboard-flow.excalidraw` (2026-11-11). Nothing here was changed: each
point needs a decision or a change outside the dashboard (data in `data/resume.db`, scripts in `src/`).

## Write actions shown disabled ("not wired yet")

The backend for these is still to be decided. Each one is visible in the UI but cannot be clicked.

| Action | Where |
|---|---|
| Mark as sent | Jobs list "…" menu, job page main button |
| New version | Jobs list "…" menu, job page "…" menu |
| Reopen | Jobs list "…" menu, job page "…" menu |
| Propose swap | Job page, "Gaps to work on" |
| Interview notes (save) | Interview prep tab, every topic card |
| Save start / end dates | Requirements page, term drawer (hard skills) |
| Change a term's type | Requirements page, term drawer |
| "+ add" keyword | Requirements page, term drawer |

## Data the wireframes ask for but the database does not hold

- **Degree requirements cannot be detected.** No field marks a requirement or interview topic as a degree, so the
  Interview prep "Quick facts" chip covers location requirements only (the `location` section in `review.json`).
- **No `education` skill type.** The `skills.type` CHECK allows technical, soft, language, location, design, ai.
  Degree terms such as "Computer Science" are typed `technical`, so they count as hard skills on the Requirements page.
- **No start dates.** 0 of 85 hard-skill entries have `start_at`, so every "your years" reads "start date needed".
- **`composed_at` and `published_at` are empty on every offer.** The job page timeline shows only "created" and "sent".
- **`cover_letter_url` is empty on every offer.** "Published cover letter →" never shows (only the resume URL exists).
- **No follow-up data.** The wireframe's "Follow up 18 Nov" / "Waiting reply" needs reply / interview / rejected
  dates that no table holds. Not built.
- **No "preview if swaps accepted".** Nothing computes coverage after proposed swaps, so it is left out of the job page.
- **No page thumbnails.** The Files card shows page counts; the documents drawer has the full PDF preview.
- **"Print a one-page cheat sheet"** (Interview prep wireframe) was not in the spec: not built.

## Data quality seen in the real jobs

- All 8 offers have `sent_at = 2026-11-11`, so "In progress", "Need you in Claude" and the average coverage card are
  empty. Check whether every one was really sent that day.
- The three Theodo jobs have no requirements, no location and no `review/interview.json`.
- `theodo-software-engineer-fullstack-v1`: company name stored as lowercase "theodo" (the other two say "Theodo").
- Every job with requirements still has all of them unreviewed (`reviewed = 0`), e.g. 38 of 38 for CGI.
- French postings add their own terms ("intelligence artificielle", "bases de données", "tests", "sécurité"), separate
  from the English ones, so the Requirements page counts "AI" and "intelligence artificielle" as two terms and "asked
  by 2+ jobs" misses them. Linking them (same skill entry) would merge their counts.

## Code outside the dashboard

- `src/paths.py`: `resume_pdf`, `cover_pdf` and `combined_pdf` call `stem()`, which calls `offers.load()` without a
  connection, so `db.connect()` opens a **writable** db and runs its ALTER migrations. `skills_inventory.load()` does
  the same. The dashboard works around both with its own read-only helpers (`dashboard/app.py`: `pdf()`,
  `inventory()`). Worth a read-only path in `src/` so other read-only tools don't trip on it.
- `.claude/skills/ats-review/SKILL.md` line 56 says each dashboard has a "Skills for application forms" box ready to
  paste. The new dashboard has no such box; the closest is Interview prep's "Skills to prepare" (posting skills with
  years). Either add the box or reword that line.

## Choices made that you may want to revisit

- **Posting drawer colours:** met terms are green, missing red, and partial terms yellow (the spec named only green and
  red).
- **"Synonym only" (Requirements page):** counts terms matched by a synonym in at least one job (7 today). Terms matched
  only by synonym in every job asking for them would be 6.
- **Stack:** Vue 3 + Element Plus front, built into `dashboard/web/dist` and served by FastAPI on port 8000, so the
  `/job/<slug>` links printed by `src/tailor.py` and `src/review_ats.py` keep working. `start.py` rebuilds on change;
  refresh the page to see it (no hot reload).
