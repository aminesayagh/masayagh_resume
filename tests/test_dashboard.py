"""Run from the repo root: .venv/bin/python -m unittest discover -s tests -t ."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard import data  # noqa: E402


def job(**kw):
    return {"slug": "x", "company": "Acme", "title": "Java Engineer", "posting": "Spring Boot microservices",
            "status": "draft", "terms": ["Java", "Spring Boot"], "location_match": "same city", **kw}


class SearchTest(unittest.TestCase):
    def test_filters_combine(self):
        jobs = [job(), job(slug="y", company="Other", title="Front-End", posting="Vue 3", status="sent",
                           terms=["Vue 3"], location_match="different country")]
        self.assertEqual([j["slug"] for j in data.search(jobs, q="acme java")], ["x"])
        self.assertEqual([j["slug"] for j in data.search(jobs, status_="sent")], ["y"])
        self.assertEqual([j["slug"] for j in data.search(jobs, skill="spring boot")], ["x"])
        self.assertEqual([j["slug"] for j in data.search(jobs, location="different")], ["y"])
        self.assertEqual(data.search(jobs, q="microservices", status_="sent"), [])


class StatusTest(unittest.TestCase):
    def test_order_sent_then_not_ready_then_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            req = [{"id": "R01", "reviewed": False}]
            self.assertEqual(data.status(folder, {"requirements": req}, {}), "draft")
            (folder / "_resume.pdf").write_bytes(b"")
            self.assertEqual(data.status(folder, {"requirements": req}, {}), "not ready")
            self.assertEqual(data.status(folder, {"requirements": req, "sent": "2026-11-11"}, {}), "sent")
            self.assertEqual(data.status(folder, {"requirements": []}, {}), "not ready")


class RequirementFilterTest(unittest.TestCase):
    def test_filters_by_text_status_and_priority(self):
        results = [{"id": "R01", "status": "met", "priority": "must_have", "description": "Java", "terms": [{"term": "Java"}]},
                   {"id": "R02", "status": "missing", "priority": "preferred", "description": "Sonar", "terms": [{"term": "Sonar"}]}]
        self.assertEqual([r["id"] for r in data.filter_requirements(results, q="sonar")], ["R02"])
        self.assertEqual([r["id"] for r in data.filter_requirements(results, status_="met")], ["R01"])
        self.assertEqual([r["id"] for r in data.filter_requirements(results, priority="preferred")], ["R02"])

    def test_files_grouped_by_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("A.pdf", "A-Cover-Letter.pdf", "A-FR.pdf", "A-FR-Cover-Letter.pdf"):
                (Path(tmp) / name).write_bytes(b"")
            groups = data.files_by_language(Path(tmp))
            self.assertEqual(groups["French"], ["A-FR-Cover-Letter.pdf", "A-FR.pdf"])
            self.assertEqual(len(groups["English"]), 2)


class ReopenTest(unittest.TestCase):
    def test_keeps_a_copy_of_the_sent_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "job.json").write_text(json.dumps({"title": "A — B", "sent": "2026-11-11"}), encoding="utf-8")
            (folder / "resume.pdf").write_bytes(b"as sent")
            archive = data.reopen(folder)
            self.assertNotIn("sent", json.loads((folder / "job.json").read_text(encoding="utf-8")))
            self.assertEqual((archive / "resume.pdf").read_bytes(), b"as sent")
            self.assertIn("2026-11-11", json.loads((archive / "job.json").read_text(encoding="utf-8"))["sent"])


class SkillsOverviewTest(unittest.TestCase):
    def test_each_job_counted_once_per_term(self):
        for row in data.skills_overview():
            self.assertEqual(row["met"] + row["partial"] + row["missing"], row["jobs"], row["term"])


class AppTest(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from dashboard.app import app
        self.client = TestClient(app)

    def test_pages_load_and_files_are_confined(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/skills").status_code, 200)
        self.assertEqual(self.client.get("/job/fictional-full-stack-v1").status_code, 200)
        self.assertEqual(self.client.get("/job/../template").status_code, 404)
        self.assertEqual(self.client.get("/files/fictional-full-stack-v1/job.json").status_code, 404)

    def test_sent_jobs_offer_no_changing_action(self):
        sent = next(p.parent.name for p in data.JOBS.glob("*/job.json")
                    if json.loads(p.read_text(encoding="utf-8")).get("sent"))
        self.assertEqual(self.client.get(f"/job/{sent}/confirm/tailor").status_code, 400)
        self.assertEqual(self.client.post(f"/job/{sent}/run/sent").status_code, 400)


if __name__ == "__main__":
    unittest.main()
