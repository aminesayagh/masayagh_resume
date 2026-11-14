#!/usr/bin/env python3
"""Resumes: every composition, with or without a job offer (the dashboard's Resumes page runs these).

Usage:
  python3 src/resumes.py new [--offer <offer id>] [--from jobs/<slug>]
      a new resume, named after the offer (its slug and PDF name, as new_job.py does) or, without one, after the resume's
      role (jobs/resume-<role>-vN): its blocs are the best candidate of each bloc
      (template/content/default.json, built by src/pick.py), composed for the offer's terms when it has one; --from
      copies another resume's choices instead (its content files), so it starts identical
  python3 src/resumes.py switch jobs/<slug> <activity id | role | summary> <candidate id> [<line position>]
      this resume uses that candidate for that bloc (the same activity's line, or a role/summary version); rebuilt.
      The position picks the line when the resume uses two lines of the same activity
  python3 src/resumes.py preview jobs/<slug> [<activity id | role | summary> <candidate id> [<line position>]]
      a temporary PDF of the resume with that candidate swapped in (nothing is changed); prints JSON {pdf, pages}
  python3 src/resumes.py edit jobs/<slug> <activity id | role | summary> "<English>" "<French>" [<line position>]
      a new version of that bloc, saved as a candidate, reviewed, and used in this resume (not when it was sent)
  python3 src/resumes.py delete jobs/<slug>
      removes a resume not written for a job offer: its folder, its record and choices, its previews; the versions
      it used stay as candidates. Refused for a job offer's resume and a sent one
  python3 src/resumes.py delete-version <summary version id>
      the version leaves the candidates (status rejected), if no in-progress resume uses it; a sent resume that used
      it keeps its record
A sent resume is frozen: switch refuses it.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import build_resume
import db
import offers
import paths
from db import EN, tr
from new_job import COPIED, JOBS_DIR, TEMPLATE_DIR, next_version, pdf_name, slugify


def create(offer_id: int | None = None, source: Path | None = None) -> Path:
    con = db.connect()
    offer = None
    if offer_id is not None:
        offer = con.execute(f"SELECT o.*, {EN.format('c.name')} AS company FROM offers o JOIN companies c "
                            "ON c.id = o.company_id WHERE o.id = ?", (offer_id,)).fetchone()
        if offer is None:
            sys.exit(f"No offer {offer_id}")
    role = json.loads((paths.content(paths.folder_arg(Path(source))) if source else TEMPLATE_DIR / "content" / "default.json")
                      .read_text(encoding="utf-8"))["role"]
    slug = f"{slugify(offer['company'])}-{slugify(offer['title'])}" if offer else f"resume-{slugify(role)}"
    version = next_version(slug)
    folder = JOBS_DIR / f"{slug}-v{version}"
    name = None if offer else f"{role} v{version}"  # a resume for an offer is named by it (the list shows its folder)
    folder.mkdir(parents=True)
    content = paths.content(folder)
    content.parent.mkdir(parents=True, exist_ok=True)
    if source:
        source = paths.folder_arg(Path(source))
        for f in COPIED:
            if (source / f).exists():
                shutil.copyfile(source / f, folder / f)
    else:
        shutil.copyfile(TEMPLATE_DIR / "content" / "default.json", content)
    person = json.loads(content.read_text(encoding="utf-8"))["name"]
    if offer:
        job = {"title": f"{offer['company']} — {offer['title']}", "offer_id": offer["id"], "posting_text": offer["posting"],
               "pdf_name": pdf_name(person, offer["title"], offer["company"])}
    else:
        job = {"title": name, "pdf_name": pdf_name(person, role)}
    offers.save(folder, job)
    con = db.connect()
    con.execute("UPDATE compositions SET name = ? WHERE folder = ?", (name, f"jobs/{folder.name}"))
    con.commit()
    db.dump(con)
    if offer and not source and offers.load(folder).get("requirements"):
        import compose  # late: compose imports build_resume
        compose.compose(folder)  # the best candidate of each bloc for this offer's terms
    build_resume.build(content)
    print(f"Created jobs/{folder.name}")
    return folder


def with_candidate(con, folder: Path, content: dict, bloc: str, candidate: int, position: int | None = None) -> dict:
    """content with one bloc's text replaced by that candidate's (an activity's line, or a role/summary version)."""
    if bloc in ("role", "summary"):
        row = con.execute("SELECT text FROM bloc_profile WHERE id = ? AND key = ?", (candidate, bloc)).fetchone()
        if row is None:
            sys.exit(f"No {bloc} version {candidate}")
        content[bloc] = tr(row[0])
        return content
    new = con.execute("SELECT text FROM bloc_descriptions WHERE id = ? AND activity_id = ? AND status = 'approved'",
                      (candidate, int(bloc))).fetchone()
    if new is None:
        sys.exit(f"No approved candidate {candidate} in activity {bloc}")
    comp = offers.composition(folder, con)
    old = con.execute("SELECT d.text FROM offer_lines l JOIN bloc_descriptions d ON d.id = l.description_id "
                      "WHERE l.composition_id = ? AND d.activity_id = ? AND (? IS NULL OR l.position = ?) ORDER BY l.position",
                      (comp["id"], int(bloc), position, position)).fetchone()
    if old is None:
        sys.exit(f"This resume has no line of activity {bloc}")
    old_text, new_text = tr(old[0]), tr(new[0])
    for e in content["experience"]:
        if e.get("description") == old_text:
            e["description"] = new_text
            return content
        if old_text in e.get("bullets", []):
            e["bullets"][e["bullets"].index(old_text)] = new_text
            return content
    sys.exit("The current line was not found in content.json; rebuild the resume first.")


def switch(folder: Path, bloc: str, candidate: int, position: int | None = None) -> None:
    """Use another candidate of one bloc in this resume: its text replaces the current one in content.json, then the
    resume is rebuilt (the build records the choice in offer_lines / composition_profile)."""
    folder = paths.folder_arg(Path(folder))
    if reason := build_resume.frozen(folder):
        sys.exit(reason)
    path = paths.content(folder)
    content = with_candidate(db.connect(), folder, json.loads(path.read_text(encoding="utf-8")), bloc, candidate, position)
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    build_resume.build(path)


def review_one(con, bloc: str, candidate: int) -> None:
    """Review one saved version, once (one Haiku call): a line with the bullet rubric, a summary with Name / Fame / Aim.
    The role has no rubric. An already reviewed, unchanged version is not reviewed again; a failed call is reported
    and leaves the version unreviewed (Review now retries it)."""
    import os
    import subprocess
    if os.environ.get("RESUME_NO_SCORING") or bloc == "role":  # tests never call the model
        return
    import score_bullet
    import score_summary
    try:
        if bloc == "summary":
            row = next((r for r in score_summary.versions(con) if r["id"] == candidate), None)
            if row is not None and score_summary.stale(row):
                score_summary.rescore(candidate, con)
        else:
            row = next((r for r in score_bullet.lines(con) if r["id"] == candidate), None)
            if row is not None and score_bullet.stale(row):
                score_bullet.rescore(candidate, con)
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as e:
        print(f"Not reviewed ({e}); use Review now to retry.")


def edit(folder: Path, bloc: str, en: str, fr: str, position: int | None = None) -> int:
    """A new version of one bloc (an activity's line, or the role / summary), written for this resume: saved as a
    candidate of the bloc (the old ones are kept), reviewed, then used by this resume. A sent resume keeps what was sent:
    the version is saved, not switched. Returns the new candidate's id."""
    import db_sync  # late, like master
    import master
    folder = paths.folder_arg(Path(folder))
    con = db.connect()
    if bloc in ("role", "summary"):
        new = con.execute(f"SELECT id FROM bloc_profile WHERE key = ? AND {EN.format('text')} = ?", (bloc, en)).fetchone()
        new = new[0] if new else master.add_profile_version(con, bloc, en, fr)
    else:
        kind = con.execute("SELECT kind FROM bloc_descriptions WHERE activity_id = ? LIMIT 1", (int(bloc),)).fetchone()
        if kind is None:
            sys.exit(f"No activity {bloc}")
        new = db_sync.add_line(con, int(bloc), kind[0], en, fr)  # an identical existing line is reused
    con.commit()
    db.dump(con)
    review_one(con, bloc, new)  # only this version: never the rest of the library's unreviewed candidates
    master.write(con)  # template/content/default*.json follow the best candidates
    if build_resume.frozen(folder):
        print(f"Saved as a new version ({new}); {folder.name} was sent, so it keeps what was sent.")
    else:
        switch(folder, bloc, new, position)
        print(f"Saved as a new version ({new}) and used in {folder.name}.")
    return new


PREVIEWS = paths.ROOT / "data" / "cache" / "preview"  # git-ignored, like the other caches; safe to delete


def preview(folder: Path, bloc: str | None = None, candidate: int | None = None, position: int | None = None) -> dict:
    """Render this resume, with one bloc's candidate swapped in if given, to a temporary PDF; the resume, its folder
    and the db are not changed (a build with an output path skips the review, the cover letter and the recording).
    Works on sent resumes too: it only reads them. Returns {pdf (file name in PREVIEWS), pages, max_pages}."""
    import hashlib
    from pypdf import PdfReader
    folder = paths.folder_arg(Path(folder))
    content = json.loads(paths.content(folder).read_text(encoding="utf-8"))
    if bloc is not None:
        content = with_candidate(db.connect(), folder, content, bloc, candidate, position)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    text = json.dumps(content, indent=2, ensure_ascii=False)
    stem = f"{folder.name}-{hashlib.sha256(text.encode()).hexdigest()[:12]}"
    data, pdf = PREVIEWS / f"{stem}.json", PREVIEWS / f"{stem}.pdf"
    if not pdf.exists():  # same content, same preview
        data.write_text(text, encoding="utf-8")
        build_resume.build(data, pdf)
    return {"pdf": pdf.name, "pages": len(PdfReader(pdf).pages), "max_pages": build_resume.MAX_PAGES}


def delete(folder: Path) -> None:
    folder = paths.folder_arg(Path(folder))
    con = db.connect()
    comp = offers.composition(folder, con)
    if comp is None:
        sys.exit(f"No resume {folder.name}")
    if comp["offer_id"] is not None or comp["sent_at"]:
        sys.exit(f"{folder.name} is written for a job offer or was sent: it is kept (the Jobs page owns it)")
    con.execute("DELETE FROM compositions WHERE id = ?", (comp["id"],))  # offer_lines and composition_profile cascade
    con.commit()
    db.dump(con)
    if folder.resolve().parent == paths.JOBS.resolve() and folder.is_dir():
        shutil.rmtree(folder)
    for f in PREVIEWS.glob(f"{folder.name}-*"):
        f.unlink()
    print(f"Deleted {folder.name}")


def delete_version(version_id: int) -> None:
    con = db.connect()
    row = con.execute("SELECT key, status FROM bloc_profile WHERE id = ?", (version_id,)).fetchone()
    if row is None or row["key"] != "summary" or row["status"] != "approved":
        sys.exit(f"No summary version {version_id} to delete")
    users = [f for (f,) in con.execute("SELECT c.folder FROM composition_profile cp JOIN compositions c ON c.id = cp.composition_id "
                                       "WHERE cp.profile_id = ? AND c.sent_at IS NULL", (version_id,))]
    if users:
        sys.exit(f"In use by {', '.join(u.removeprefix('jobs/') for u in users)}; switch it there first")
    con.execute("UPDATE bloc_profile SET status = 'rejected' WHERE id = ?", (version_id,))
    con.commit()
    db.dump(con)
    import master  # late, like edit
    master.write(con)  # the resume files follow the remaining candidates
    print(f"Summary version {version_id} deleted")


def main() -> None:
    if sys.argv[1:2] == ["new"]:
        p = argparse.ArgumentParser(prog="resumes.py new")
        p.add_argument("--offer", type=int)
        p.add_argument("--from", dest="source")
        a = p.parse_args(sys.argv[2:])
        create(a.offer, a.source)
    elif len(sys.argv) in (5, 6) and sys.argv[1] == "switch":
        switch(Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) == 6 else None)
    elif len(sys.argv) in (3, 5, 6) and sys.argv[1] == "preview":
        bloc, cand, pos = (sys.argv[3:] + [None, None, None])[:3]
        out = preview(Path(sys.argv[2]), bloc, int(cand) if cand else None, int(pos) if pos else None)
        print("PREVIEW " + json.dumps(out))
    elif len(sys.argv) == 3 and sys.argv[1] == "delete":
        delete(Path(sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == "delete-version" and sys.argv[2].isdigit():
        delete_version(int(sys.argv[2]))
    elif len(sys.argv) in (6, 7) and sys.argv[1] == "edit":
        edit(Path(sys.argv[2]), sys.argv[3], sys.argv[4].strip(), sys.argv[5].strip(), int(sys.argv[6]) if len(sys.argv) == 7 else None)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
