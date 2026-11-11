#!/usr/bin/env python3
"""Publish a job's tailored resume PDF to the portfolio site.

Usage: python3 src/publish_resume.py jobs/<slug>/job.json

Copies jobs/<slug>/<pdf_name> to public/resume/<company>/<pdf_name> in
the portfolio repo, commits only that file, and pushes to main. Vercel deploys it to
https://www.masayagh.com/resume/<company>/<pdf_name> in about a minute, so a
download keeps the PDF's real name. Every update replaces the PDF at that link.

Works in a dedicated clone (PUBLISH_CLONE), never in /home/amine/projects/portfolio:
that shared working copy is often on a feature branch with uncommitted work.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PORTFOLIO = Path("/home/amine/projects/portfolio")
PUBLISH_CLONE = Path("/home/amine/projects/portfolio-publish")  # ponytail: owned by this script only
SITE = "https://www.masayagh.com"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(PUBLISH_CLONE), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def publish(job_path: Path) -> str:
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if job.get("sent"):
        sys.exit(f"{job_path.parent.name} was sent on {job['sent']}; the published copy stays as sent.")
    company = job.get("company")
    if not (isinstance(company, str) and re.fullmatch(r"[a-z0-9-]+", company)):
        sys.exit(f"{job_path} needs 'company' ([a-z0-9-]+) to publish.")
    pdf = job_path.parent / job.get("pdf_name", "resume.pdf")
    if not pdf.exists():
        draft = pdf.with_name("_" + pdf.name)
        sys.exit(f"Not published: only {draft.name} exists, which is NOT READY to send (see the build warnings)."
                 if draft.exists() else f"{pdf} does not exist; build it first.")

    if not PUBLISH_CLONE.exists():
        url = subprocess.run(["git", "-C", str(PORTFOLIO), "remote", "get-url", "origin"],
                             check=True, capture_output=True, text=True).stdout.strip()
        subprocess.run(["git", "clone", "--quiet", url, str(PUBLISH_CLONE)], check=True)
    # The clone is ours alone, so resetting it to origin/main loses nothing.
    git("fetch", "--quiet", "origin", "main")
    git("checkout", "--quiet", "-B", "main", "origin/main")

    # Version 2+ of a job gets its own folder, so the copy an employer received under v1 never changes.
    n = int(m[1]) if (m := re.search(r"-v(\d+)$", job_path.parent.name)) else 1
    version_dir = f"v{n}/" if n > 1 else ""
    # The English resume and its English cover letter are published; the French version (-FR) stays local.
    cover = pdf.with_name(f"{pdf.stem}-Cover-Letter.pdf")  # a not-ready letter is '_'-prefixed, so it's skipped
    files = [pdf] + ([cover] if cover.exists() else [])
    if not cover.exists():
        print(f"Cover letter not published: {cover.name} is missing or NOT READY.")
    for f in files:
        rel = f"public/resume/{company}/{version_dir}{f.name}"  # ponytail: a renamed pdf_name leaves the old file; git rm it by hand
        target = PUBLISH_CLONE / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target)
        git("add", "--", rel)
    url = f"{SITE}/resume/{company}/{version_dir}{pdf.name}"
    if not git("diff", "--cached", "--name-only"):
        print(f"Already published, unchanged: {url}")
        return url
    git("commit", "--quiet", "-m", f"Publish resume {company}/{pdf.name}")
    git("pull", "--quiet", "--rebase", "origin", "main")  # others push to main too
    git("push", "--quiet", "origin", "HEAD:main")
    print(f"Pushed {', '.join(f.name for f in files)} to main; live in about a minute at {url}"
          + (f" and {SITE}/resume/{company}/{version_dir}{cover.name}" if cover in files else ""))
    return url


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    publish(Path(sys.argv[1]))
