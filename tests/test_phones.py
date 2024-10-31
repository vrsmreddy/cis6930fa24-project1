
import unittest

from redactor import redact_phones

class TestPhonesRedaction(unittest.TestCase):
    def test_standard_phone(self):
        text = "Call me at (123) 456-7890."
        expected = "Call me at ██████████████."
        redacted_text, count = redact_phones(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)

    def test_dashed_phone(self):
        text = "My number is 123-456-7890."
        expected = "My number is ████████████."
        redacted_text, count = redact_phones(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)

    def test_dotted_phone(self):
        text = "Office: 123.456.7890."
        expected = "Office: ████████████."
        redacted_text, count = redact_phones(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)

    def test_plain_phone(self):
        text = "Emergency number is 1234567890."
        expected = "Emergency number is ██████████."
        redacted_text, count = redact_phones(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 1)

    def test_invalid_phone(self):
        text = "This is not a phone number: 12345."
        expected = text  # Should not be redacted
        redacted_text, count = redact_phones(text)
        self.assertEqual(redacted_text, expected)
        self.assertEqual(count, 0)

if __name__ == '__main__':
    unittest.main()
