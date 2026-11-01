"""Run: .venv/bin/python -m unittest test_check_style"""

import unittest

import check_style


class CheckStyleTest(unittest.TestCase):
    def test_rules(self):
        content = {
            "summary": "I build software for my clients.",
            "experience": [{"company": "X,", "description": "Helped the team ship features.", "bullets": [
                "Built a billing service used by 40 clients.",
                "Built " + "very " * 30 + "long bullet.",
                "Built dashboards.",
            ]}],
        }
        codes = [f["code"] for f in check_style.check(content)["findings"]]
        self.assertEqual(codes.count("first_person"), 1)
        self.assertIn("weak_opener", codes)
        self.assertIn("too_long", codes)
        self.assertIn("repeated_opener", codes)
        measurable = next(f for f in check_style.check(content)["findings"] if f["code"] == "measurable")
        self.assertIn("1 of 4", measurable["message"])

    def test_clean_content_has_no_warnings(self):
        content = {"summary": "Developer who ships reliable web products.",
                   "experience": [{"company": "X", "description": "Shipped a portal for 3 banks.", "bullets": []}]}
        self.assertEqual([f for f in check_style.check(content)["findings"] if f["severity"] == "warning"], [])


if __name__ == "__main__":
    unittest.main()
