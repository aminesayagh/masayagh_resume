"""Personal settings: config.json at the repo root (ignored by git; see config.example.json).

Without config.json everything works and nothing is published (publish.mode = "none").
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "config.json"
DEFAULTS = {
    "publish": {
        "mode": "none",               # none | folder | git
        "repo": "",                   # git: the portfolio repo (its remote is cloned into "clone")
        "clone": "",                  # git: a clone only this pipeline uses (default: <repo>-publish)
        "branch": "main",             # git: branch to push
        "folder": "",                 # folder: where PDFs are copied
        "path": "resume/{company}/{file}",  # where a file goes, inside the repo or folder
        "site": "",                   # base address of the published files, if any
        "url": "{site}/resume/{company}/{file}",  # public link of a file ("" = no link)
    },
}


def load() -> dict:
    user = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    return {key: {**value, **user.get(key, {})} for key, value in DEFAULTS.items()}


def publish() -> dict:
    return load()["publish"]


def public_url(company: str, file: str, settings: dict | None = None) -> str | None:
    """The link a published file gets (the same for every version of an application), or None when nothing is
    published or no address is set."""
    p = settings or publish()
    if p["mode"] == "none" or not p["url"] or ("{site}" in p["url"] and not p["site"]):
        return None
    return p["url"].format(site=p["site"].rstrip("/"), company=company, file=file)


assert public_url("acme", "a.pdf", {**DEFAULTS["publish"]}) is None
assert public_url("acme", "a.pdf", {**DEFAULTS["publish"], "mode": "git", "site": "https://x.dev/"}) == \
    "https://x.dev/resume/acme/a.pdf"
