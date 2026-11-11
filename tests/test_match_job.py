"""Run from the repo root: .venv/bin/python -m unittest discover -s tests -t ."""

import json
import unittest
from pathlib import Path

from pypdf import PdfReader

import check_pdf
import db
import match_job

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = ["Summary", "Technical Proficiencies", "Professional Experience", "Academic Education"]
PAGES = [
    "Jane Doe\nCasablanca, Morocco\nSummary\nDeveloper who builds Docker tooling.\nTechnical\nProficiencies\n"
    "Python PostgreSQL Kubernetes\nProfessional\nExperience\nJan 2020 - Dec 2022\nAcme\n"
    "Built Python services and integrated APIs with automated\ntesting in CI.\n"
    "Academic\nEducation\nBachelor's in Computer Science",
]


def req(rid, terms, **kw):
    return {"id": rid, "section": "requirement", "priority": "must_have", "quote": "q", "description": rid,
            "terms": terms, "reviewed": True, **kw}


def run(reqs, content=None, aliases=None):
    report = match_job.assess({"requirements": reqs}, PAGES, content, HEADINGS, aliases or {})
    return {r["id"]: r for r in report["results"]}


class MatchJobTest(unittest.TestCase):
    def test_sections_are_detected(self):
        lines = {l["text"]: l["section"] for l in match_job.pdf_lines(PAGES, HEADINGS)}
        self.assertEqual(lines["Casablanca, Morocco"], "header")
        self.assertEqual(lines["Developer who builds Docker tooling."], "summary")
        self.assertEqual(lines["Python PostgreSQL Kubernetes"], "skills")
        self.assertEqual(lines["Acme"], "experience")
        self.assertEqual(lines["Bachelor's in Computer Science"], "education")

    def test_evidence_levels(self):
        r = run([req("exp", ["Python"]), req("skills", ["Kubernetes"]), req("summary", ["Docker"]),
                 req("none", ["TypeScript"]), req("edu", ["computer science"]), req("loc", ["Morocco"])])
        self.assertEqual(r["exp"]["status"], "met")
        self.assertEqual(r["exp"]["quote"], "Built Python services and integrated APIs with automated")
        self.assertEqual(r["skills"]["status"], "partial")
        self.assertEqual(r["skills"]["keyword"], "exact")   # recruiter search still sees it
        self.assertEqual(r["summary"]["status"], "partial")
        self.assertEqual((r["none"]["status"], r["none"]["keyword"], r["none"]["quote"]), ("missing", "absent", None))
        self.assertEqual(r["edu"]["status"], "met")
        self.assertEqual(r["loc"]["status"], "met")

    def test_word_boundaries_and_line_breaks(self):
        r = run([req("sql", ["SQL"]), req("split", ["automated testing"])])
        self.assertEqual(r["sql"]["status"], "missing")   # 'PostgreSQL' is not 'SQL'
        self.assertEqual(r["split"]["status"], "met")
        self.assertEqual(r["split"]["quote"], "Built Python services and integrated APIs with automated testing in CI.")

    def test_alias_is_reported_as_wording_differs(self):
        r = run([req("pg", ["Postgres"]), req("api", ["API integration"])],
                aliases={"api integration": ["integrated APIs"]})
        self.assertEqual(r["pg"]["status"], "missing")   # no alias given for Postgres -> PostgreSQL
        self.assertEqual((r["api"]["status"], r["api"]["keyword"]), ("met", "alias"))
        self.assertIn("Wording differs", r["api"]["rationale"])

    def test_multi_term_is_partial(self):
        r = run([req("mix", ["Python", "TypeScript"])])
        self.assertEqual(r["mix"]["status"], "partial")
        self.assertEqual(r["mix"]["keyword"], "some")

    def test_years(self):
        content = lambda *dates: {"experience": [{"company": f"C{i}", "dates": d} for i, d in enumerate(dates)]}
        y = lambda n, c: run([req("y", [], kind="years_experience", min_years=n)], c)["y"]
        self.assertEqual(y(3, content("Jan 2020 - Dec 2022"))["status"], "met")
        self.assertEqual(y(3, content("Jan 2020 - Dec 2022"))["quote"], "Jan 2020 - Dec 2022")
        self.assertEqual(y(3, content("Jan 2020 - Dec 2021", "Jan 2020 - Dec 2021"))["status"], "partial")
        self.assertEqual(y(5, content("Jan 2020 - Dec 2022"))["status"], "missing")
        self.assertEqual(y(3, content("sometime"))["status"], "uncertain")
        self.assertEqual(y(3, None)["status"], "uncertain")

    def test_real_pdf_quotes_are_verbatim_and_deterministic(self):
        job = json.loads((ROOT / "jobs" / "fictional-full-stack-v1" / "job.json").read_text(encoding="utf-8"))
        content = json.loads((ROOT / "template" / "content" / "default.json").read_text(encoding="utf-8"))
        pages = [p.extract_text() for p in PdfReader(ROOT / "template" / "build" / "resume.pdf").pages]
        aliases = db.aliases()
        headings = check_pdf.template_headings(check_pdf.TEMPLATE)
        first = match_job.assess(job, pages, content, headings, aliases)
        self.assertEqual(first, match_job.assess(job, pages, content, headings, aliases))
        for r in first["results"]:
            if r["status"] in ("met", "partial"):
                self.assertIsNotNone(r["quote"], r["id"])
                page = " ".join(pages[r["page"] - 1].split())
                self.assertIn(" ".join(r["quote"].split()), page, r["id"])


if __name__ == "__main__":
    unittest.main()
