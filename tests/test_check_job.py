"""Run from the repo root: .venv/bin/python -m unittest discover -s tests -t ."""

import copy
import json
import unittest
from pathlib import Path

import check_job

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "jobs" / "fictional-full-stack-v1" / "job.json").read_text(encoding="utf-8"))


def errors(job, **kw):
    return {f["code"] for f in check_job.validate(job, **kw) if f["severity"] == "error"}


def with_req(**changes):
    job = copy.deepcopy(FIXTURE)
    job["requirements"][0].update(changes)
    return job


class CheckJobTest(unittest.TestCase):
    def test_fixture_is_valid(self):
        self.assertEqual(errors(FIXTURE), set())

    def test_quote_must_be_verbatim(self):
        self.assertIn("quote_not_found", errors(with_req(quote="Build beautiful React apps.")))
        self.assertIn("quote_missing", errors(with_req(quote="")))
        # whitespace and line breaks do not matter
        self.assertNotIn("quote_not_found", errors(with_req(quote="Design  and integrate\nAPIs backed by PostgreSQL.",
                                                           terms=["PostgreSQL"])))

    def test_terms_use_posting_wording(self):
        self.assertIn("term_not_in_quote", errors(with_req(terms=["Postgres"])))

    def test_unreviewed_fails_unless_draft(self):
        job = with_req(reviewed=False)
        self.assertIn("unreviewed", errors(job))
        self.assertNotIn("unreviewed", errors(job, draft=True))

    def test_no_hard_gate_from_soft_wording(self):
        job = copy.deepcopy(FIXTURE)
        aws = next(r for r in job["requirements"] if r.get("terms") == ["AWS"])
        aws["priority"] = "must_have"
        self.assertIn("soft_gate", errors(job))
        posting = {"title": "t", "posting_text": "Docker experience is a plus.", "requirements": [
            {"id": "R1", "section": "requirement", "priority": "must_have", "quote": "Docker experience is a plus.",
             "description": "Docker", "terms": ["Docker"], "reviewed": True}]}
        self.assertIn("soft_gate", errors(posting))

    def test_shape_errors(self):
        job = copy.deepcopy(FIXTURE)
        job["requirements"][1]["id"] = job["requirements"][0]["id"]
        self.assertIn("id_duplicate", errors(job))
        self.assertIn("priority", errors(with_req(priority="required")))
        self.assertIn("unknown_field", errors(with_req(revieved=True)))
        self.assertIn("min_years", errors(with_req(kind="years_experience")))
        self.assertIn("posting", errors({"title": "t", "posting_file": "nope.txt", "requirements": FIXTURE["requirements"]}))


if __name__ == "__main__":
    unittest.main()
