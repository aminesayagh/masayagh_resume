"""Run from the repo root: .venv/bin/python -m unittest discover -s tests -t ."""

import copy
import json
import unittest
from pathlib import Path

import check_job
import review_ats

ROOT = Path(__file__).resolve().parents[1]
JOB = json.loads((ROOT / "tests" / "fixtures" / "fictional-job.json").read_text(encoding="utf-8"))
CONTENT = json.loads((ROOT / "template" / "content" / "default.json").read_text(encoding="utf-8"))
PDF = ROOT / "template" / "build" / "resume.pdf"


def run(job):
    return review_ats.review(job, PDF, CONTENT, network=False)


class ReviewTest(unittest.TestCase):
    def test_override_keeps_automated_finding_and_flags_stale(self):
        job = copy.deepcopy(JOB)
        job["overrides"] = [
            {"id": "R04", "status": "met", "reason": "Docker and CI/CD used daily at Phoenix AI",
             "pdf_quote": "Data scraping CI/CD Docker Testing Practices"},
            {"id": "R11", "status": "partial", "reason": "Wrote tests at Cogy Tech", "pdf_quote": "A line that is not in the PDF"},
            {"id": "R14", "status": "missing", "reason": "Agree, no AWS", "pdf_quote": None},
        ]
        self.assertEqual([f for f in check_job.validate(job) if f["severity"] == "error"], [])
        rep = run(job)
        r = {x["id"]: x for x in rep["results"]}
        self.assertEqual((r["R04"]["status"], r["R04"]["automated"]["status"], r["R04"]["override"]["stale"]),
                         ("met", "partial", False))
        self.assertTrue(r["R11"]["override"]["stale"])
        self.assertFalse(r["R14"]["override"]["stale"])
        self.assertEqual(rep["overridden"], 3)
        md = review_ats.markdown(rep, {"cv": "a", "job": "b", "content": "c"})
        self.assertIn("Automated finding: partial", md)
        self.assertIn("**R11** override is **stale**", md)

    def test_invalid_overrides_fail_validation(self):
        job = copy.deepcopy(JOB)
        job["overrides"] = [{"id": "R99", "status": "met", "reason": "x"},
                            {"id": "R07", "status": "great", "reason": ""}]
        codes = {f["code"] for f in check_job.validate(job)}
        self.assertTrue({"override_id", "override_status", "override_reason"} <= codes)

    def test_suggestions_are_rule_based(self):
        rep = run(JOB)
        r = {x["id"]: x for x in rep["results"]}
        partial = next(x for x in rep["results"] if x["status"] == "partial")  # any: depends on template wording
        self.assertIn("only in your skills list", partial["suggestion"])
        missing = next(x for x in rep["results"] if x["status"] == "missing")  # any: depends on template wording
        self.assertIn("does not appear", missing["suggestion"])
        self.assertIn("The posting says 'APIs'", r["R02"]["suggestion"])   # wording differs
        self.assertIsNone(r["R12"]["suggestion"])                         # met, exact

    def test_coverage_formula_and_report_order(self):
        rep = run(JOB)
        must = [x for x in rep["results"] if x["priority"] == "must_have"]
        met, partial = (sum(x["status"] == s for x in must) for s in ("met", "partial"))
        self.assertEqual(rep["evidence_coverage"]["must_have"], round((met + 0.5 * partial) / len(must), 2))
        md = review_ats.markdown(rep, {"cv": "a", "job": "b", "content": "c"})
        order = [md.index(h) for h in ("## Decisions for you", "## 1. PDF readability", "## 2. Content checks",
                                       "## 3. Must-have", "## 4. Preferred", "## Summary")]
        self.assertEqual(order, sorted(order))
        self.assertIn("not an ATS score", md)


if __name__ == "__main__":
    unittest.main()
