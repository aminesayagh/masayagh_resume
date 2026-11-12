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

REPO = Path(__file__).resolve().parent.parent


class FreshDb:
    """A temporary db (never data/resume.db) holding the master resume, loaded from copies of default*.json."""

    def __enter__(self):
        import shutil
        import db
        import master
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.saved = (db.DB, db.DUMP, dict(master.FILES), master.STAMP)
        db.DB, db.DUMP = self.root / "test.db", self.root / "test.sql"
        for lang, path in dict(master.FILES).items():
            shutil.copyfile(path, self.root / path.name)
            master.FILES[lang] = self.root / path.name
        master.STAMP = self.root / "stamp.json"
        master.import_files(db.connect(empty=True))
        return self.root

    def __exit__(self, *exc):
        import db
        import master
        db.DB, db.DUMP, files, master.STAMP = self.saved
        master.FILES.update(files)
        self.tmp.cleanup()


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
        (self.job / "pdf" / "A-Resume-and-Cover-Letter.pdf").write_bytes(b"resume+letter")
        self.saved = config.FILE
        config.FILE = root / "config.json"

    def tearDown(self):
        self.config.FILE = self.saved
        self.db.DB, self.db.DUMP = self.saved_db
        self.tmp.cleanup()

    def test_none_publishes_nothing(self):
        self.assertIsNone(self.publish.publish(self.job / "job.json"))  # no config.json at all

    def test_folder_copies_every_version_to_the_same_link(self):
        out = Path(self.tmp.name) / "out"
        self.config.FILE.write_text(self.json.dumps({"publish": {
            "mode": "folder", "folder": str(out), "site": "https://x.dev"}}), encoding="utf-8")
        url = self.publish.publish(self.job / "job.json")
        self.assertEqual((out / "resume/acme/A.pdf").read_bytes(), b"resume+letter")  # one PDF, the resume's link
        self.assertEqual([p.name for p in (out / "resume/acme").iterdir()], ["A.pdf"])
        self.assertEqual(url, "https://x.dev/resume/acme/A.pdf")
        (self.job / "pdf" / "A-Resume-and-Cover-Letter.pdf").rename(self.job / "pdf" / "_A-Resume-and-Cover-Letter.pdf")
        self.publish.publish(self.job / "job.json")  # letter not ready: the resume alone
        self.assertEqual((out / "resume/acme/A.pdf").read_bytes(), b"resume")

    def test_sent_jobs_are_never_published(self):
        self.offers.save(self.job, {**self.offer, "sent": "2026-11-11"})
        self.config.FILE.write_text(self.json.dumps({"publish": {"mode": "folder", "folder": self.tmp.name}}), encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.publish.publish(self.job / "job.json")


class RecordBuildTest(unittest.TestCase):
    def test_each_part_keeps_its_own_warnings(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            build_resume.record_build(folder, "resume", ["skills have 4 rows."], False)
            build_resume.record_build(folder, "cover", [], True)
            build_resume.record_build(folder, "resume", [], True)  # a rebuild replaces only its own entry
            data = json.loads((folder / "review" / "build.json").read_text(encoding="utf-8"))
            self.assertEqual((data["resume"]["warnings"], data["resume"]["ready"]), ([], True))
            self.assertTrue(data["cover"]["ready"])


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



class SkillTypesTest(unittest.TestCase):
    """skills_inventory's type command and dates for hard skills only. Temporary dbs only."""

    def setUp(self):
        import db
        self.db, self.tmp = db, tempfile.TemporaryDirectory()
        self.saved = (db.DB, db.DUMP)
        root = Path(self.tmp.name)
        db.DB, db.DUMP = root / "test.db", root / "test.sql"  # never the real data/resume.db

    def tearDown(self):
        self.db.DB, self.db.DUMP = self.saved
        self.tmp.cleanup()

    def run_cli(self, *args):
        argv = sys.argv
        sys.argv = ["skills_inventory.py", *args]
        try:
            skills_inventory.main()
        finally:
            sys.argv = argv

    def test_type_command_and_dates_for_hard_skills_only(self):
        self.db.connect().close()
        self.run_cli("type", "communication", "soft")  # a new term gets an entry with that type
        with self.assertRaises(SystemExit):  # only hard skills have dates
            self.run_cli("set", "communication", "2020-01")
        with self.assertRaises(SystemExit):
            self.run_cli("type", "communication", "nonsense")
        self.run_cli("type", "Git", "technical")
        self.run_cli("set", "Git", "2016-03", "2024-06")
        self.run_cli("type", "Git", "education")  # leaving the hard types drops the dates
        con = self.db.connect()
        rows = {r[0]: tuple(r[1:]) for r in con.execute(
            "SELECT json_extract(name, '$.en'), type, start_at, end_at FROM skills")}
        self.assertEqual(rows, {"communication": ("soft", None, None), "git": ("education", None, None)})
        self.assertTrue(self.db.DUMP.exists())  # resume.sql (here test.sql) refreshed after each change



class MarkSentTest(unittest.TestCase):
    """offers.py sent: records the day, and refuses a second time or a future day."""

    def test_mark_sent_on_a_temporary_db(self):
        import offers
        with FreshDb() as root:
            job = root / "acme-dev-v1"
            offers.save(job, {"title": "Acme — Dev", "posting_text": "Build things.", "pdf_name": "A.pdf"})
            with self.assertRaises(SystemExit):
                offers.mark_sent(job, "2999-01-01")  # never in the future
            self.assertEqual(offers.mark_sent(job, "2026-11-10"), "2026-11-10")
            self.assertEqual(offers.load(job)["sent"], "2026-11-10")
            with self.assertRaises(SystemExit):
                offers.mark_sent(job)  # already sent
            import db
            self.assertTrue(db.DUMP.exists())  # resume.sql (here test.sql) refreshed


class MasterTest(unittest.TestCase):
    """The master resume is generated from the db; hand edits are refused, db edits regenerate both files."""

    def setUp(self):
        import master
        self.master, self.fresh = master, FreshDb()
        self.fresh.__enter__()

    def tearDown(self):
        self.fresh.__exit__()

    def test_hand_edit_is_refused(self):
        path = self.master.FILES["en"]
        path.write_text(path.read_text(encoding="utf-8").replace("Software", "Hardware", 1), encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.master.write()

    def test_db_edit_regenerates_both_languages(self):
        self.master.set_value(["role", "Platform Engineer", "Ingénieur plateforme"])
        import json
        self.assertEqual(json.loads(self.master.FILES["en"].read_text(encoding="utf-8"))["role"], "Platform Engineer")
        self.assertEqual(json.loads(self.master.FILES["fr"].read_text(encoding="utf-8"))["role"], "Ingénieur plateforme")


class ComposeOnceTest(unittest.TestCase):
    """compose.py picks each activity's line for the offer, writes text only, never recomposes a job; an agreed edit
    joins its activity; a new version is composed again and gets the newest wording."""

    def test_first_composition_only(self):
        import json
        import shutil
        import compose
        import db
        import db_sync
        import offers
        import paths
        with FreshDb() as root:
            con = db.connect()
            base = "Integrated an AI agent experience that transforms"
            aid = con.execute(f"SELECT activity_id FROM descriptions WHERE {db.EN.format('text')} LIKE ?", (base + "%",)).fetchone()[0]
            variant = "Integrated Large Language Models into an AI agent that configures marketing campaigns."
            db_sync.add_line(con, aid, "bullet", variant)  # a second approved wording of the same activity
            con.commit()
            folder = root / "acme-dev-v1"
            paths.content(folder).parent.mkdir(parents=True)
            shutil.copyfile(REPO / "template/content/default.json", paths.content(folder))
            offers.save(folder, {"title": "Acme — Dev", "posting_text": "Large Language Models and APIs.",
                                 "requirements": [{"id": "R01", "section": "requirement", "priority": "must_have",
                                                   "quote": "Large Language Models and APIs.", "terms": ["Large Language Models"]}]})
            compose.compose(folder)
            content = json.loads(paths.content(folder).read_text(encoding="utf-8"))
            hypeo = next(e for e in content["experience"] if e["company"].startswith("Phoenix"))
            self.assertNotIn("activities", hypeo)  # the JSON holds text only
            self.assertIn(variant, hypeo["bullets"])  # the variant with the offer's term
            with self.assertRaises(SystemExit):
                compose.compose(folder)  # already composed: refused
            i = hypeo["bullets"].index(variant)  # an agreed edit: new wording; the db works out its activity
            hypeo["bullets"][i] = variant.replace("Integrated", "Shipped")
            paths.content(folder).write_text(json.dumps(content), encoding="utf-8")
            db_sync.sync_job(folder)
            find = f"SELECT activity_id FROM descriptions WHERE {db.EN.format('text')} = ?"
            self.assertEqual(db.connect().execute(find, (hypeo["bullets"][i],)).fetchone()[0], aid)
            import new_job  # a new version: same offer, lines composed again from the library
            saved_new = (new_job.JOBS_DIR, new_job.ROOT, new_job.build_resume.build)
            new_job.JOBS_DIR, new_job.ROOT, new_job.build_resume.build = root, root.parent, lambda *a, **k: None
            try:
                v2 = new_job.new_version(folder)
            finally:
                new_job.JOBS_DIR, new_job.ROOT, new_job.build_resume.build = saved_new
            self.assertEqual(v2.name, "acme-dev-v2")
            self.assertEqual(offers.load(v2)["offer_id"], offers.load(folder)["offer_id"])  # one offer, two compositions
            v2_hypeo = next(e for e in json.loads(paths.content(v2).read_text(encoding="utf-8"))["experience"]
                            if e["company"].startswith("Phoenix"))
            self.assertIn(hypeo["bullets"][i], v2_hypeo["bullets"])  # the agreed edit, now the newest line
            self.assertEqual(json.loads(paths.content(folder).read_text(encoding="utf-8")), content)  # v1 untouched


if __name__ == "__main__":
    unittest.main()
