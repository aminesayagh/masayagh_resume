"""Run: .venv/bin/python -m unittest test_check_spelling"""

import unittest

import check_spelling


def flagged(content, allow=()):
    return {f["word"]: f for f in check_spelling.check(content, [], set(allow))["findings"]}


class CheckSpellingTest(unittest.TestCase):
    def test_typo_is_a_warning_with_suggestion(self):
        found = flagged({"summary": "I developped reliable sofware."})
        self.assertEqual(found["developped"]["severity"], "warning")
        self.assertIn("developed", found["developped"]["suggestions"])
        self.assertIn("sofware", found)
        self.assertNotIn("reliable", found)

    def test_names_terms_and_allowlist_are_not_flagged(self):
        content = {
            "company": "Zorblax",
            "skills": [["Kubeflow"]],
            "summary": "Built Zorblax and Kubeflow tools with FastAPI, Next.js and SaaS workflows.",
            "contact": {"email": "x@qwzx.com"},
        }
        self.assertEqual(flagged(content, {"workflow"}), {})


if __name__ == "__main__":
    unittest.main()
