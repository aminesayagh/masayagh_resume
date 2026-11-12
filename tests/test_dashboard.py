"""Run from the repo root: .venv/bin/python -m unittest discover -s tests -t ."""

import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard import app  # noqa: E402


def job(**kw):
    return {"status": "in progress", "sent": None, "must_have": 0.5, "warnings": 0, **kw}


class ReadOnlyTest(unittest.TestCase):
    @unittest.skipUnless(app.DB.exists(), "no data/resume.db")
    def test_connection_refuses_writes(self):
        with app.ro() as con:
            with self.assertRaises(sqlite3.OperationalError):
                con.execute("CREATE TABLE dashboard_probe (x)")


class CardsTest(unittest.TestCase):
    def test_counts_and_average_from_open_jobs_only(self):
        jobs = [job(must_have=0.6, warnings=2), job(must_have=None), job(status="sent", sent="2026-11-01", must_have=1.0),
                job(status="sent", sent="2026-09-01")]
        self.assertEqual(app.cards(jobs, today=date(2026, 11, 11)),
                         {"in_progress": 2, "with_warnings": 1, "sent_30_days": 1, "avg_must_have": 0.6})

    def test_nothing_to_average(self):
        self.assertIsNone(app.cards([job(status="sent", sent="2026-11-01")])["avg_must_have"])


class BuildNotesTest(unittest.TestCase):
    def test_warnings_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "acme-dev-v1"
            review = {"pdf_check": {"pages": [{}] * 4, "findings": [{"severity": "info", "code": "meta_author", "message": "m"}]},
                      "style": {"findings": [{"severity": "warning", "code": "new_code", "message": "w"}]}}
            notes = app.build_notes(folder, {"requirements": [{}], "french_version": True}, review)
        self.assertEqual([n["severity"] for n in notes], ["warning"] * 3 + ["info"])
        texts = [n["text"] for n in notes]
        self.assertIn("Resume is 4 pages (target 3)", texts)
        self.assertIn("Posting is in French: French version needed", texts)
        self.assertTrue(all(set(n) == {"severity", "text"} for n in notes))  # warnings only, no advice

    def test_build_json_says_why_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "acme-dev-v1"
            (folder / "pdf").mkdir(parents=True)
            (folder / "pdf" / "_resume.pdf").write_bytes(b"")  # not ready, no build.json yet: the fallback line
            texts = lambda: [n["text"] for n in app.build_notes(folder, {"requirements": [{}]}, {})]
            self.assertEqual(texts(), ["Resume marked not ready ('_' file)"])
            (folder / "review").mkdir()
            (folder / "review" / "build.json").write_text(json.dumps({
                "resume": {"built": "2026-11-11T20:15", "ready": False, "warnings": ["skills have 4 rows"]},
                "cover": {"built": "2026-11-11T20:15", "ready": True, "warnings": ["long paragraph"]}}))
            notes = app.build_notes(folder, {"requirements": [{}]}, {})
        self.assertEqual([(n["severity"], n["text"]) for n in notes],
                         [("warning", "Resume not ready: skills have 4 rows"), ("info", "Cover letter: long paragraph")])

    def test_no_requirements(self):
        notes = app.build_notes(Path("/nonexistent"), {}, {})
        self.assertEqual(notes, [{"severity": "warning", "text": "No requirements yet"}])


@unittest.skipUnless(app.DB.exists(), "no data/resume.db")
class ApiTest(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        self.client = TestClient(app.app)

    def test_jobs_are_real_and_status_is_binary(self):
        body = self.client.get("/api/jobs").json()
        with app.ro() as con:
            self.assertEqual(len(body["jobs"]), con.execute("SELECT count(*) FROM offers").fetchone()[0])
        self.assertTrue({j["status"] for j in body["jobs"]} <= {"in progress", "sent"})
        self.assertNotIn("ats score", json.dumps(body).lower())

    def test_never_opens_a_writable_db(self):
        """src/db.connect() migrates and can restore the db; every page must go through app.ro() instead."""
        import db
        from unittest import mock
        with mock.patch.object(db, "connect", side_effect=AssertionError("db.connect() called")):
            for job in self.client.get("/api/jobs").json()["jobs"]:
                self.assertEqual(self.client.get(f"/api/jobs/{job['slug']}").status_code, 200)
                self.assertEqual(self.client.get(f"/api/jobs/{job['slug']}/interview").status_code, 200)
            self.assertEqual(self.client.get("/api/requirements").status_code, 200)

    def test_interview_prep_is_the_saved_file(self):
        for job in self.client.get("/api/jobs").json()["jobs"]:
            prep = self.client.get(f"/api/jobs/{job['slug']}/interview").json()
            saved = app.load_json(app.paths.interview(app.paths.JOBS / job["slug"]))
            self.assertEqual(prep["exists"], bool(saved))
            self.assertEqual(len(prep["topics"]), len(saved.get("topics", [])))
            for focus, n in prep["summary"].items():  # the three cards are real counts
                self.assertEqual(n, sum(t["focus"] == focus for t in prep["topics"]))
            self.assertTrue(all(s["years"] for s in prep["skills"]))  # "start date needed" when there is none

    def test_job_detail_matches_its_review(self):
        slug = next(j["slug"] for j in self.client.get("/api/jobs").json()["jobs"] if j["has_requirements"])
        d = self.client.get(f"/api/jobs/{slug}").json()
        review = app.load_json(app.paths.review_json(app.paths.JOBS / slug))
        self.assertEqual(len(d["requirements"]), len(review["results"]))
        must = d["coverage"]["must_have"]
        self.assertEqual(must["met"] + must["partial"] + must["missing"] + must["uncertain"], must["total"])
        self.assertTrue(all(g["status"] != "met" for g in d["gaps"]))
        self.assertEqual([g["priority"] for g in d["gaps"]], sorted((g["priority"] for g in d["gaps"]),
                                                                       key=lambda p: p != "must_have"))
        self.assertEqual(self.client.get("/api/jobs/no-such-job").status_code, 404)

    def test_requirement_terms_follow_the_db(self):
        d = self.client.get("/api/requirements").json()
        with app.ro() as con:
            distinct = {t.casefold() for (t,) in con.execute("SELECT term FROM requirement_terms")}
            untyped = {t.casefold() for (t,) in con.execute("SELECT term FROM requirement_terms WHERE skill_id IS NULL")}
        self.assertEqual({t["term"].casefold() for t in d["terms"]}, distinct)
        self.assertEqual({t["term"].casefold() for t in d["terms"] if not t["type"]}, untyped)
        for t in d["terms"]:
            self.assertEqual(t["jobs"], len(t["asked"]))
            self.assertLessEqual(t["met"] + t["partial"] + t["missing"], t["jobs"])
            self.assertEqual(t["hard"], t["type"] in app.HARD)
            if t["hard"]:
                self.assertTrue(t["experience"])  # years, or "start date needed"
            else:
                self.assertIsNone(t["experience"])  # soft, language, location: no dates, no level
            self.assertEqual(t["synonym"], any(a["wording"] == "synonym" for a in t["asked"]))
        self.assertLessEqual(d["hard_with_start"], d["hard_entries"])

    def test_new_version_runs_the_script(self):
        """The script is mocked: the test never creates a job. It checks the command, the parsing and the guards."""
        from unittest import mock
        slug = app.offers.all_folders(app.ro())[0].name
        done = mock.Mock(returncode=0, stdout=f"Created jobs/{slug}-copy from {slug} (not sent; ...)\n", stderr="")
        with mock.patch.object(app.subprocess, "run", return_value=done) as run:
            body = self.client.post(f"/api/jobs/{slug}/new-version").json()
        self.assertEqual(run.call_args.args[0][1:], ["src/new_job.py", "--from", f"jobs/{slug}"])
        self.assertEqual((body["ok"], body["slug"]), (True, f"{slug}-copy"))

        failed = mock.Mock(returncode=1, stdout="", stderr="Traceback ...")
        with mock.patch.object(app.subprocess, "run", return_value=failed):
            body = self.client.post(f"/api/jobs/{slug}/new-version").json()
        self.assertEqual((body["ok"], body["slug"], body["output"]), (False, None, "Traceback ..."))

        with mock.patch.object(app.subprocess, "run") as run:
            self.assertEqual(self.client.post("/api/jobs/no-such-job/new-version").status_code, 404)
            with app.WRITE_LOCK:  # one already running
                self.assertEqual(self.client.post(f"/api/jobs/{slug}/new-version").status_code, 409)
            run.assert_not_called()

    def test_term_drawer_writes_go_through_skills_inventory(self):
        """The script is mocked: nothing is written. Checks validation, guards and the exact commands."""
        from unittest import mock
        ok = mock.Mock(returncode=0, stdout="done\n", stderr="")
        hard = {"name_en": "Git", "type": "technical"}
        with mock.patch.object(app.subprocess, "run", return_value=ok) as run:
            post = self.client.post
            self.assertEqual(post("/api/skills/type", json={"term": "communication", "type": "soft"}).json()["ok"], True)
            self.assertEqual(run.call_args.args[0][1:], ["src/skills_inventory.py", "type", "communication", "soft"])
            self.assertEqual(post("/api/skills/type", json={"term": "x", "type": "nonsense"}).status_code, 422)
            self.assertEqual(post("/api/skills/type", json={"term": "a\nb", "type": "soft"}).status_code, 422)

            with mock.patch.object(app, "skill_named", return_value=hard):
                post("/api/skills/dates", json={"skill": "Git", "start": "2016-03", "end": "2024-06"})
                self.assertEqual(run.call_args.args[0][1:], ["src/skills_inventory.py", "set", "Git", "2016-03", "2024-06"])
                for bad in ({"start": "2016-13"}, {"start": "March 2016"}, {"start": "2024", "end": "2016"}):
                    self.assertEqual(post("/api/skills/dates", json={"skill": "Git", **bad}).status_code, 422, bad)
            with mock.patch.object(app, "skill_named", return_value={"name_en": "communication", "type": "soft"}):
                self.assertEqual(post("/api/skills/dates", json={"skill": "communication", "start": "2020"}).status_code, 422)
            with mock.patch.object(app, "skill_named", return_value=None):  # no entry: type it first
                self.assertEqual(post("/api/skills/dates", json={"skill": "x", "start": "2020"}).status_code, 404)
                self.assertEqual(post("/api/skills/keyword", json={"skill": "x", "keyword": "y"}).status_code, 404)
            calls = run.call_count

            with app.ro() as con:  # a keyword already used by a skill is refused
                taken = con.execute("SELECT s.name_en, k.keyword, k.lang FROM skill_keywords k "
                                    "JOIN skills s ON s.id = k.skill_id LIMIT 1").fetchone()
            if taken:
                with mock.patch.object(app, "skill_named", return_value=hard):
                    r = post("/api/skills/keyword", json={"skill": "Git", "keyword": taken[1].upper(), "lang": taken[2]})
                self.assertEqual(r.status_code, 409)
            self.assertEqual(run.call_count, calls)  # refused requests ran nothing

    def test_skills_redirects_to_requirements(self):
        r = self.client.get("/skills", follow_redirects=False)
        self.assertEqual((r.status_code, r.headers["location"]), (301, "/requirements"))

    def test_files_stay_inside_the_job_folder(self):
        from fastapi import HTTPException
        slug = app.offers.all_folders(app.ro())[0].name
        for name in ("../../data/resume.db", "content/content.json"):  # outside the folder, or not a .pdf/.md
            with self.assertRaises(HTTPException):
                app.files(slug, name)


if __name__ == "__main__":
    unittest.main()
