# test_names.py

import unittest
from redactor import redact_names  
class TestRedactNames(unittest.TestCase):

    

    def test_email_redaction(self):
        text = "Contact me at john.doe@example.com for more information."
        expected_output = "Contact me at ████████████████████ for more information."
        redacted_text, _ = redact_names(text)
        self.assertEqual(redacted_text, expected_output)

    def test_metadata_redaction(self):
        text = """
        X-From: Jane Doe
        X-To: jdoe <john.doe@example.com>
        X-Origin: Doe-J
        """
        expected_output = """
        X-From: ████████
        X-To: ████ <████████████████████>
        X-Origin: █████
        """
        redacted_text, _ = redact_names(text)
        self.assertEqual(redacted_text.strip(), expected_output.strip())

    def test_x_filename_redaction(self):
        text = "X-FileName: jdoe (Non-Privileged).pst"
        expected_output = "X-FileName: ████ (Non-Privileged).pst"
        redacted_text, _ = redact_names(text)
        self.assertEqual(redacted_text, expected_output)

    def test_x_folder_redaction(self):
        text = "X-Folder: \\Doe_John\\Inbox"
        expected_output = "X-Folder: \\████████\\Inbox"
        redacted_text, _ = redact_names(text)
        self.assertEqual(redacted_text, expected_output)

    def test_date_preservation(self):
        text = "Date: Mon, 14 May 2001 16:39:00 -0700 (PDT)"
        expected_output = "Date: Mon, 14 May 2001 16:39:00 -0700 (PDT)"
        redacted_text, _ = redact_names(text)
        self.assertEqual(redacted_text, expected_output)

    

if __name__ == '__main__':
    unittest.main()