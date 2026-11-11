#!/usr/bin/env python3
"""Publish a job's English resume and cover letter, as set in config.json ("publish").

Usage: python3 src/publish_resume.py jobs/<slug>

Modes (config.example.json documents them):
  none    nothing is published (the default, no config.json needed)
  folder  the PDFs are copied into a local folder, e.g. one a static host or a sync tool serves
  git     the PDFs are committed to a portfolio repository and pushed, through a clone only this script uses
          (never the repository's own working copy, which may hold other work)
In every mode: sent (frozen) jobs, not-ready ('_') resumes and the French version are never published.
One file is sent: the resume with its cover letter in the same PDF when the letter is ready, else the resume alone.
An application has one public link: every version publishes to the same place, so the link always serves the
latest version.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import config
import db
import paths
import offers


def git(clone: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(clone), *args], check=True, capture_output=True, text=True).stdout.strip()


def files_to_publish(job_path: Path, job: dict) -> tuple[str, list[Path]]:
    """(company, [the PDF to send]) or exit with the reason it can't be published. The PDF is the resume and cover
    letter combined when that file is ready, else the resume alone; it is always sent under the resume's name."""
    if job.get("sent"):
        sys.exit(f"{job_path.parent.name} was sent on {job['sent']}; the published copy stays as sent.")
    company = job.get("company")
    if not (isinstance(company, str) and re.fullmatch(r"[a-z0-9-]+", company)):
        sys.exit(f"{job_path} needs 'company' ([a-z0-9-]+) to publish.")
    pdf = paths.resume_pdf(job_path.parent)
    if not pdf.exists():
        draft = paths.not_ready(pdf)
        sys.exit(f"Not published: only {draft.name} exists, which is NOT READY to send (see the build warnings)."
                 if draft.exists() else f"{pdf} does not exist; build it first.")
    combined = paths.combined_pdf(job_path.parent)  # '_'-prefixed unless both resume and letter are ready
    if combined.exists():
        return company, [combined]
    print(f"Resume sent without a cover letter: {combined.name} is missing or NOT READY.")
    return company, [pdf]


def place(settings: dict, company: str, file: str) -> str:
    return settings["path"].format(company=company, file=file)


def publish(job_path: Path) -> str | None:
    settings = config.publish()
    if settings["mode"] == "none":
        print("Publishing is off (no config.json, or publish.mode = none): the PDFs stay in the job folder.")
        return None
    job_path = paths.job(paths.folder_arg(job_path))
    job = offers.load(job_path.parent)
    company, files = files_to_publish(job_path, job)
    name = paths.resume_pdf(job_path.parent).name  # the application's one link, whatever the PDF holds

    if settings["mode"] == "folder":
        root = Path(settings["folder"]).expanduser()
        target = root / place(settings, company, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(files[0], target)
        print(f"Copied {files[0].name} to {target}")
    elif settings["mode"] == "git":
        repo = Path(settings["repo"]).expanduser()
        clone = Path(settings["clone"]).expanduser() if settings["clone"] else repo.with_name(repo.name + "-publish")
        branch = settings["branch"]
        if not clone.exists():
            remote = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"],
                                    check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "clone", "--quiet", remote, str(clone)], check=True)
        git(clone, "fetch", "--quiet", "origin", branch)  # the clone is ours alone: resetting it loses nothing
        git(clone, "checkout", "--quiet", "-B", branch, f"origin/{branch}")
        rel = place(settings, company, name)  # ponytail: a renamed pdf_name leaves the old file
        (clone / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(files[0], clone / rel)
        git(clone, "add", "--", rel)
        if git(clone, "diff", "--cached", "--name-only"):
            git(clone, "commit", "--quiet", "-m", f"Publish resume {company}/{name}")
            git(clone, "pull", "--quiet", "--rebase", "origin", branch)  # others may push too
            git(clone, "push", "--quiet", "origin", f"HEAD:{branch}")
            print(f"Pushed {files[0].name} as {name} to {branch}")
        else:
            print("Already published, unchanged.")
    else:
        sys.exit(f"config.json: unknown publish.mode '{settings['mode']}' (none, folder or git).")

    urls = [config.public_url(company, name, settings)]
    con = db.connect()  # the links the employer gets, kept with the offer
    con.execute("UPDATE offers SET resume_url = ?, cover_letter_url = ?, published_at = date('now') WHERE folder = ?",
                (urls[0], urls[1] if len(urls) > 1 else None, f"jobs/{job_path.parent.name}"))
    con.commit()
    db.dump(con)
    for u in urls:
        if u:
            print(f"  {u}")
    return urls[0]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    publish(Path(sys.argv[1]))
