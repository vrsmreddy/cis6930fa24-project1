# test_dates.py

import unittest
import textwrap
from redactor import redact_dates  # Ensure 'redact_dates.py' is in the same directory or adjust the import accordingly

class TestDatesRedaction(unittest.TestCase):

    def test_day_name(self):
        text = "Meeting is scheduled on Monday."
        # "Monday" has 6 characters
        redacted_part = '█' * len("Monday")  # 6 '█'
        expected = f"Meeting is scheduled on {redacted_part}."
        redacted_text, count = redact_dates(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)  # One redaction for "Monday"

    def test_duration(self):
        text = "The project will take 3 weeks to complete."
        expected = "The project will take 3 weeks to complete."
        redacted_text, count = redact_dates(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 0)  # Duration should not be redacted

    def test_iso_date(self):
        text = "The deadline is 2025-12-31."
        # "2025-12-31" has 10 characters
        redacted_part = '█' * len("2025-12-31")  # 10 '█'
        expected = f"The deadline is {redacted_part}."
        redacted_text, count = redact_dates(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)  # One redaction for "2025-12-31"

    def test_standard_date(self):
        text = "The event is on 12/25/2025."
        # "12/25/2025" has 10 characters
        redacted_part = '█' * len("12/25/2025")  # 10 '█'
        expected = f"The event is on {redacted_part}."
        redacted_text, count = redact_dates(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)  # One redaction for "12/25/2025"

    def test_written_date(self):
        text = "We met on April 5th, 2020."
        # "April 5th, 2020" has 15 characters
        redacted_part = '█' * len("April 5th, 2020")  # 15 '█'
        expected = f"We met on {redacted_part}."
        redacted_text, count = redact_dates(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)  # One redaction for "April 5th, 2020"

if __name__ == '__main__':
    unittest.main()
