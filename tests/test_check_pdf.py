"""Run from the repo root: .venv/bin/python -m unittest discover -s tests -t ."""

import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfWriter

import check_pdf

ROOT = Path(__file__).resolve().parents[1]


def codes(report, severity):
    return {f["code"] for f in report["findings"] if f["severity"] == severity}


class CheckPdfTest(unittest.TestCase):
    def test_image_only_pdf_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "blank.pdf"
            writer = PdfWriter()
            writer.add_blank_page(612, 792)
            writer.write(pdf)
            self.assertIn("no_text", codes(check_pdf.check(pdf, None, []), "error"))

    def test_corrupt_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "broken.pdf"
            pdf.write_bytes(b"not a pdf")
            self.assertIn("unreadable", codes(check_pdf.check(pdf, None, []), "error"))

    def test_default_resume_has_all_critical_fields(self):
        content = json.loads((ROOT / "template" / "default.json").read_text(encoding="utf-8"))
        headings = check_pdf.template_headings(check_pdf.TEMPLATE)
        report = check_pdf.check(ROOT / "template" / "resume.pdf", content, headings)
        self.assertEqual(codes(report, "error"), set())
        self.assertIn("Experience", headings)
        self.assertFalse(any("<br" in h for h in headings))

    def test_missing_field_is_an_error(self):
        content = {"name": "Nobody Atall", "contact": {}, "experience": [], "education": []}
        report = check_pdf.check(ROOT / "template" / "resume.pdf", content, [])
        self.assertIn("field_missing", codes(report, "error"))

    def test_dates_years_overlap_and_single_date(self):
        found = []
        years = check_pdf.check_dates({"experience": [
            {"company": "Zed", "dates": "Jan 2020 - Dec 2021"},  # name order != date order
            {"company": "Alpha", "dates": "Jan 2021 - Dec 2022"},  # overlaps Zed by a year
            {"company": "C", "dates": "Aug 2023"},              # single month
            {"company": "D", "dates": "Mar 2024 - Jan 2024"},   # reversed
        ]}, lambda sev, code, msg, **kw: found.append(code))
        self.assertEqual(years, {"merged": round(37 / 12, 1), "summed": round(49 / 12, 1)})
        self.assertTrue({"date_overlap", "date_single", "date_order"} <= set(found))

    def test_contact_icon_only_links_and_phone(self):
        found = []
        content = {"contact": {"email": "a@b.com", "phone": "0612345678", "linkedin": "https://linkedin.com/in/x"}}
        check_pdf.check_contact(content, "a@b.com", {"https://linkedin.com/in/x"},
                                lambda sev, code, msg, **kw: found.append(code), network=False)
        self.assertEqual(found, ["phone_country", "link_icon_only"])

    def test_default_pdf_file_name_warns(self):
        content = json.loads((ROOT / "template" / "default.json").read_text(encoding="utf-8"))
        report = check_pdf.check(ROOT / "template" / "resume.pdf", content, [])
        self.assertIn("file_name", codes(report, "warning"))
        self.assertNotIn("meta_title", codes(report, "warning"))


if __name__ == "__main__":
    unittest.main()
