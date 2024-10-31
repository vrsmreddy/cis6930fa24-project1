
import unittest
import textwrap
from redactor import redact_addresses

class TestRedactAddresses(unittest.TestCase):

    def test_address_in_signature(self):
        text = textwrap.dedent("""
            From: someone@example.com
            To: recipient@example.com

            Best regards,
            John Doe
            ABC Corporation
            123 Main Street, 5th Floor
            Springfield, IL 62704
            """)
        # Original address lines:
        # "123 Main Street, 5th Floor" -> 24 characters
        # "Springfield, IL 62704" -> 22 characters
        redacted_line1 = '█' * len('123 Main Street, 5th Floor')  # 24 '█'
        redacted_line2 = '█' * len('Springfield, IL 62704')      # 22 '█'

        expected_output = textwrap.dedent(f"""
            From: someone@example.com
            To: recipient@example.com

            Best regards,
            John Doe
            ABC Corporation
            {redacted_line1}
            {redacted_line2}
            """)

        redacted_text, _ = redact_addresses(text)
        self.assertEqual(redacted_text.strip(), expected_output.strip())

    def test_address_in_body(self):
        text = textwrap.dedent("""
            Please send the documents to the following address:

            456 Elm Street
            Anytown, CA 90210

            Thank you.
            """)
        # Original address lines:
        # "456 Elm Street" -> 14 characters
        # "Anytown, CA 90210" -> 18 characters
        redacted_line1 = '█' * len('456 Elm Street')        # 14 '█'
        redacted_line2 = '█' * len('Anytown, CA 90210')    # 18 '█'

        expected_output = textwrap.dedent(f"""
            Please send the documents to the following address:

            {redacted_line1}
            {redacted_line2}

            Thank you.
            """)

        redacted_text, _ = redact_addresses(text)
        self.assertEqual(redacted_text.strip(), expected_output.strip())

    def test_no_address(self):
        text = textwrap.dedent("""
            Hello,

            There is no address in this email.

            Best,
            Jane
            """)
        expected_output = textwrap.dedent("""
            Hello,

            There is no address in this email.

            Best,
            Jane
            """)
        redacted_text, _ = redact_addresses(text)
        self.assertEqual(redacted_text.strip(), expected_output.strip())

if __name__ == '__main__':
    unittest.main()