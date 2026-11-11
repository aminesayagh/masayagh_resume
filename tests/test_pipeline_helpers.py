import http.server
import sys
import threading
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import check_pdf  # noqa: E402
import build_resume  # noqa: E402
import check_job  # noqa: E402
import check_spelling  # noqa: E402
import draft_job  # noqa: E402,F401  (its asserts check line numbering, quotes and candidates)
import fetch_posting  # noqa: E402,F401  (its asserts check the JobPosting parsing)
import review_ats  # noqa: E402
import tailor  # noqa: E402
import compose  # noqa: E402,F401  (its asserts check the pick: most offer terms, ties to the newest)
import build_fr  # noqa: E402,F401  (its asserts check French-only posting detection)
import skills_inventory  # noqa: E402,F401  (its asserts check skill splitting and year math)


class PublishModesTest(unittest.TestCase):
    """Runs publish_resume for real in modes none and folder, against a temporary config and job."""

    def setUp(self):
        import json
        import config
        import publish_resume
        self.json, self.config, self.publish = json, config, publish_resume
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        import db
        import offers
        self.db, self.offers = db, offers
        self.saved_db = (db.DB, db.DUMP)
        db.DB, db.DUMP = root / "test.db", root / "test.sql"  # never the real data/resume.db
        self.job = root / "acme-dev-v2"
        (self.job / "pdf").mkdir(parents=True)
        self.offer = {"title": "Acme — Dev", "posting_text": "Build things.", "company": "acme", "pdf_name": "A.pdf"}
        offers.save(self.job, self.offer)
        (self.job / "pdf" / "A.pdf").write_bytes(b"resume")
        (self.job / "pdf" / "A-Cover-Letter.pdf").write_bytes(b"letter")
        self.saved = config.FILE
        config.FILE = root / "config.json"

    def tearDown(self):
        self.config.FILE = self.saved
        self.db.DB, self.db.DUMP = self.saved_db
        self.tmp.cleanup()

    def test_none_publishes_nothing(self):
        self.assertIsNone(self.publish.publish(self.job / "job.json"))  # no config.json at all

    def test_folder_copies_resume_and_letter_under_the_version(self):
        out = Path(self.tmp.name) / "out"
        self.config.FILE.write_text(self.json.dumps({"publish": {
            "mode": "folder", "folder": str(out), "site": "https://x.dev"}}), encoding="utf-8")
        url = self.publish.publish(self.job / "job.json")
        self.assertEqual((out / "resume/acme/v2/A.pdf").read_bytes(), b"resume")
        self.assertTrue((out / "resume/acme/v2/A-Cover-Letter.pdf").exists())
        self.assertEqual(url, "https://x.dev/resume/acme/v2/A.pdf")

    def test_sent_jobs_are_never_published(self):
        self.offers.save(self.job, {**self.offer, "sent": "2026-11-11"})
        self.config.FILE.write_text(self.json.dumps({"publish": {"mode": "folder", "folder": self.tmp.name}}), encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.publish.publish(self.job / "job.json")


class AddAllowTest(unittest.TestCase):
    def test_appends_on_new_line_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "allow.txt"
            path.write_text("Fullstack", encoding="utf-8")  # no final newline: the bug that made "FullstackOdoo"
            check_spelling.add_allow(["Odoo", "Fullstack", "Odoo"], path)
            self.assertEqual(path.read_text(encoding="utf-8"), "Fullstack\nOdoo\n")


class CompareTest(unittest.TestCase):
    def test_flags_lost_terms_and_extra_pages(self):
        base = {"terms": {("R01", "APIs"): "met", ("R02", "SQL"): "missing"},
                "must_have": 0.5, "preferred": 0.1, "pages": 3, "spelling": 0, "pdf": 0}
        new = {**base, "terms": {("R01", "APIs"): "partial", ("R02", "SQL"): "met"}, "must_have": 0.6, "pages": 4}
        changes, regressions = review_ats.compare(base, new)
        self.assertIn("R02 SQL: missing → met", changes)
        self.assertEqual(regressions, ["R01 APIs: met → partial", "pages 3 → 4"])


class LinkCheckTest(unittest.TestCase):
    def test_broken_link_warns_and_mailto_is_skipped(self):
        server = http.server.HTTPServer(("127.0.0.1", 0), http.server.SimpleHTTPRequestHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            found = []
            check_pdf.check_links({f"http://127.0.0.1:{server.server_port}/no-such-page", "mailto:a@b.co"},
                                  lambda severity, code, message: found.append((severity, code)))
            self.assertEqual(found, [("warning", "link_broken")])
        finally:
            server.shutdown()


class InterviewTest(unittest.TestCase):
    def test_topics_carry_review_facts_in_priority_order(self):
        term = lambda name, status, quote=None: {"term": name, "status": status, "keyword": "exact", "quote": quote}
        rep = {"title": "Acme — Dev", "generated": "2026-11-09", "results": [
            {"id": "R02", "priority": "preferred", "status": "missing", "description": "Go", "quote": "Go", "terms": [term("Go", "missing")]},
            {"id": "R01", "priority": "must_have", "status": "met", "description": "APIs", "quote": "APIs",
             "terms": [term("APIs", "met", "Built APIs")]},
            {"id": "R03", "priority": "must_have", "status": "partial", "description": "SQL", "quote": "SQL",
             "terms": [term("SQL", "partial", "Skills: SQL")]},
        ]}
        sheet = review_ats.interview(rep, {"requirements": [{"id": "R01", "quote": "Design APIs."}]})
        self.assertEqual(sheet["topics"][1]["posting_says"], "Design APIs.")
        self.assertEqual([(t["id"], t["focus"]) for t in sheet["topics"]],
                         [("R03", "prove_claim"), ("R01", "prepare_story"), ("R02", "gap")])
        self.assertEqual(sheet["topics"][1]["your_resume_says"], ["Built APIs"])
        self.assertEqual(sheet["topics"][2]["terms_not_met"], ["Go"])


class TitleCheckTest(unittest.TestCase):
    def test_warns_when_resume_title_differs(self):
        job = {"title": "Y Strategie — Senior Front-End Developer", "requirements": []}
        self.assertFalse(review_ats.title_check(job, {"role": "Software Engineer"})["match"])
        self.assertTrue(review_ats.title_check(job, {"role": "Senior Front End Developer"})["match"])
        self.assertTrue(review_ats.title_check(job, {"role": "Front-End Engineer"})["match"])  # seniority, dev = engineer
        self.assertFalse(review_ats.title_check(job, {"role": "Back-End Engineer"})["match"])


class SkillsLayoutTest(unittest.TestCase):
    def test_six_rows_with_template_counts(self):
        rows = [[f"s{r}{i}" for i in range(4)] for r in range(6)]
        self.assertIsNone(build_resume.skills_problem(rows))
        self.assertIn("rows", build_resume.skills_problem(rows[:4]))
        self.assertIn("per row", build_resume.skills_problem(rows[:5] + [rows[5] + ["extra"]]))


class TargetsTest(unittest.TestCase):
    def test_bad_targets_rejected_and_gaps_listed(self):
        job = {"title": "A — B", "posting_text": "Experience with Vue 3.", "requirements": [
            {"id": "R01", "section": "requirement", "priority": "must_have", "quote": "Experience with Vue 3.",
             "description": "Vue", "terms": ["Vue 3"], "targets": ["skills", "cover letter"], "reviewed": True}]}
        self.assertIn("targets", {f["code"] for f in check_job.validate(job)})
        rep = {"results": [{"id": "R01", "priority": "must_have", "targets": ["skills", "experience"],
                            "terms": [{"term": "Vue 3", "found_in": ["skills"], "missing_from": ["experience"]}]}]}
        self.assertEqual(review_ats.placement_gaps(rep)[0]["missing_from"], ["experience"])


class GapTableTest(unittest.TestCase):
    def test_lists_every_unmet_term_and_skips_met(self):
        review = {"results": [
            {"id": "R01", "priority": "must_have", "status": "met", "terms": [{"term": "APIs", "status": "met"}]},
            {"id": "R02", "priority": "preferred", "status": "partial", "terms": [
                {"term": "cloud", "status": "met", "missing_from": []},
                {"term": "automation", "status": "missing", "missing_from": ["skills", "experience"]}]}]}
        rows = tailor.gap_table(review)
        self.assertEqual(len(rows), 3)
        self.assertIn("automation | missing | skills, experience", rows[2])


if __name__ == "__main__":
    unittest.main()
