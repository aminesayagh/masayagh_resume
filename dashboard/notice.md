# Dashboard: open points to work on later

Found while rebuilding the dashboard from `dashboard-flow.excalidraw` (2026-11-11). Nothing here was changed: each
point needs a decision or a change outside the dashboard (data in `data/resume.db`, scripts in `src/`).

## Write actions

No disabled action is left. **Dropped (2026-11-12):** the job page's "Gaps to work on" card and its "Propose swap"
button (the Skills tab lists every requirement with its hint).

**Wired (2026-11-12): Interview notes.** Each topic card's box saves with its Save button (no autosave), through
`src/offers.py note jobs/<slug> "<keyword>" ["text"]` (empty deletes). One note per requirement of the offer
(`interview_notes`), so every version of the job shares it and sent jobs work (the folder is not touched). A topic is
matched to its requirement by keyword ("java (10+ years)" -> java), so a years topic shares its keyword's note.

**Wired:** New version (jobs list and job page "…" menus) runs `src/new_job.py --from jobs/<slug>` after a
confirmation, then opens the new job. One run at a time (server lock). **Dropped:** Reopen (not needed).

**Wired (2026-11-12): Mark as sent** (jobs list "…" menu, job page button) runs `src/offers.py sent jobs/<slug> [date]`
after you pick the day (today by default, never in the future). It records `sent_at` and snapshots the review's
results; the job is then frozen. Sent jobs show "Sent on <date>" instead.

**Wired (2026-11-12): the Requirements term drawer**, through `src/skills_inventory.py`:
- Type: `type "<term>" <type>`; a term with no entry gets one. Leaving the hard types drops the dates.
- Start / end dates (hard skills only): `set "<skill>" <start> [<end>]`; the dashboard checks the format and order first.
- "+ add" keyword (en or fr): `keyword "<skill>" "<keyword>" <lang>`; only once the term has a type, and refused when
  the keyword already counts as another skill.
- Merge (2026-11-12): "Merge into another skill" runs `move "<keyword>" "<skill>"`: the keyword joins the chosen skill
  (and takes its type); the old skill is dropped once it has no keyword left (its resume-line and cover-paragraph links
  go to the target; its dates are not carried over). Every job asking for it gets its review recomputed, sent ones included (only their review/ reports change).
- Since the offer / composition schema (2026-11-12), a requirement points to a keyword, which belongs to one skill, so a
  type or keyword added later shows on every job.

## Data the wireframes ask for but the database does not hold

- **Education type added (2026-11-12),** but existing degree terms such as "Computer Science" are still typed
  `technical`: change them to education in the term drawer.
- **No start dates.** 0 of 85 hard-skill entries have `start_at`, so every "your years" reads "start date needed".
- **Timeline:** the schema keeps only the offer's `created_at` ("posting saved"), the composition's `created_at`
  ("version created") and `sent_at`. `composed_at`, `published_at` and `cover_letter_url` were dropped (the cover
  letter is inside the published PDF), so "Published cover letter →" never shows.
- **No follow-up data.** The wireframe's "Follow up 18 Nov" / "Waiting reply" needs reply / interview / rejected
  dates that no table holds. Not built.
- **No "preview if swaps accepted".** Nothing computes coverage after proposed swaps, so it is left out of the job page.
- **No page thumbnails.** The Files card shows page counts; the documents drawer has the full PDF preview.
- **"Print a one-page cheat sheet"** (Interview prep wireframe) was not in the spec: not built.

## Data quality seen in the real jobs (before 2026-11-12)

The offers and compositions were dropped on 2026-11-12 (only the master resume was re-imported), so the points below
apply to the 8 old job folders only, which have no rows in the db any more.

- All 8 offers have `sent_at = 2026-11-11`, so "In progress", "With warnings" and the average coverage card are
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
- **Stack:** Vue 3 + Element Plus front, built into `dashboard/web/dist` and served by FastAPI on port 8765, so the
  `/job/<slug>` links printed by `src/tailor.py` and `src/review_ats.py` keep working. `start.py` rebuilds on change;
  refresh the page to see it (no hot reload).
