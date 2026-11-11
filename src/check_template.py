#!/usr/bin/env python3
"""Check whether template/content/default.json is ready to start a new job application.

Usage: python3 src/check_template.py

Rebuilds template/build/resume.pdf from template/content/default.json and runs the spelling,
style and PDF-readability checks against it -- the same gate src/new_job.py runs
before scaffolding a new jobs/<slug>/ folder, so you can see what to fix without
having to start (and abandon) a new application first.
Exit code: 0 = ready (no findings), 1 = not ready (findings listed).
"""

import hashlib
import json
from pathlib import Path

import build_resume
import offers
import paths
import review_ats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE_DIR = ROOT / "template"
NON_BLOCKING_TEMPLATE_CODES = {"file_name"}


def check() -> list[dict]:
    """Spelling/style/PDF-readability findings against the template baseline, if
    any. Reuses review_ats.review() with an empty-requirements job so it only
    runs the content checks, not job matching. "info" findings don't block."""
    import master  # the master resume lives in data/resume.db; default.json / default-fr.json are generated
    master.write()
    content_path = TEMPLATE_DIR / "content" / "default.json"
    pdf_path = build_resume.build(content_path, TEMPLATE_DIR / "build" / "resume.pdf")
    content = json.loads(content_path.read_text(encoding="utf-8"))
    # network=True: every link in the PDF is opened; a broken one (HTTP 4xx/5xx) blocks, being offline doesn't
    rep = review_ats.review({"title": "template baseline", "requirements": []}, pdf_path, content, network=True)
    findings = rep["pdf_check"]["findings"] + rep["spelling"]["findings"] + rep["style"]["findings"]
    if len(rep["pdf_check"]["pages"]) > build_resume.MAX_PAGES:
        findings.append({"severity": "error", "code": "page_count",
                         "message": f"resume.pdf has {len(rep['pdf_check']['pages'])} pages; the limit is {build_resume.MAX_PAGES}"})
    if problem := build_resume.skills_problem(content["skills"]):
        findings.append({"severity": "error", "code": "skills_layout", "message": problem})
    # template/build/resume.pdf is the repository's canonical internal artifact name,
    # not the filename sent to a recruiter. Keep the upload-name warning in the
    # general PDF checker, but do not let it block creation of a job workspace.
    return [
        f for f in findings
        if f["severity"] != "info" and f.get("code") not in NON_BLOCKING_TEMPLATE_CODES
    ]


def stale_jobs() -> list[Path]:
    """Job folders whose content.json is still the untouched template copy (its hash equals
    the offer's template_sha) but the template has changed since. Safe to refresh."""
    current = hashlib.sha256((TEMPLATE_DIR / "content" / "default.json").read_bytes()).hexdigest()
    stale = []
    for folder in offers.all_folders():
        job = offers.load(folder)
        sha = None if job.get("sent") else job.get("template_sha")  # sent jobs are frozen
        content = paths.content(folder)
        if sha and sha != current and content.exists() and hashlib.sha256(content.read_bytes()).hexdigest() == sha:
            stale.append(folder)
    return stale


def main() -> None:
    findings = check()
    if not findings:
        print("template/ is ready: no spelling, style or PDF-readability findings.")
        for folder in stale_jobs():
            print(f"Untailored job behind the template (safe to refresh): {folder.relative_to(ROOT)}")
        return
    print(f"template/ is not ready: {len(findings)} finding(s) to fix first.\n")
    for f in findings:
        print(f"[{f['severity']}] {f['message']}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
