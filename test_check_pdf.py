"""Run: .venv/bin/python -m unittest test_check_pdf"""

import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfWriter

import check_pdf

HERE = Path(__file__).resolve().parent


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
        content = json.loads((HERE / "content" / "default.json").read_text(encoding="utf-8"))
        headings = check_pdf.template_headings(check_pdf.TEMPLATE)
        report = check_pdf.check(HERE / "output" / "default.pdf", content, headings)
        self.assertEqual(codes(report, "error"), set())
        self.assertIn("Professional Experience", headings)
        self.assertFalse(any("<br" in h for h in headings))

    def test_missing_field_is_an_error(self):
        content = {"name": "Nobody Atall", "contact": {}, "experience": [], "education": []}
        report = check_pdf.check(HERE / "output" / "default.pdf", content, [])
        self.assertIn("field_missing", codes(report, "error"))


if __name__ == "__main__":
    unittest.main()
