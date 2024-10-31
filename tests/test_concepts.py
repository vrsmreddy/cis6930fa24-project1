# tests/test_concepts.py

import unittest
import textwrap
from redactor import redact_concepts  # Adjust the import path as necessary
from redactor import sentence_model, nlp, REDACTION_CHAR  # Ensure these are accessible

class TestConceptsRedaction(unittest.TestCase):

    def test_exact_concept_match(self):
        """
        Test that sentences containing the exact concept are redacted.
        """
        text = textwrap.dedent("""
            The conference will be held in New York next month.
            We are excited about the upcoming event.
            Make sure to register early.
        """)
        concepts = ["conference"]
        
        # Expected output: First sentence redacted
        redacted_sentence = ''.join(REDACTION_CHAR for _ in "The conference will be held in New York next month.")
        expected = textwrap.dedent(f"""
            {redacted_sentence}
            We are excited about the upcoming event.
            Make sure to register early.
        """).strip()
        
        redacted_text, count = redact_concepts(text, concepts)
        self.assertEqual(redacted_text.strip(), expected)
        self.assertEqual(count, 1)  # One sentence redacted

    
    def test_no_concept_match(self):
        """
        Test that sentences without the concept or its synonyms remain unchanged.
        """
        text = textwrap.dedent("""
            The weather today is sunny and bright.
            Let's plan for a picnic this weekend.
            Remember to bring sunscreen and water.
        """)
        concepts = ["conference"]
        
        # Expected output: No changes
        expected = textwrap.dedent("""
            The weather today is sunny and bright.
            Let's plan for a picnic this weekend.
            Remember to bring sunscreen and water.
        """).strip()
        
        redacted_text, count = redact_concepts(text, concepts)
        self.assertEqual(redacted_text.strip(), expected)
        self.assertEqual(count, 0)  # No sentences redacted
    
    def test_house_concept_redaction(self):
        """
        Test that sentences containing the concept 'house' and its synonym 'mansion' are redacted.
        """
        input_text = textwrap.dedent("""
            Jack pursued his journey. He walked on till after sunset, when to his great joy, he espied a large mansion. A plain-looking woman was at the door: he accosted her, begging she would give him a morsel of bread and a night’s lodging. She expressed the greatest surprise, and said it was quite uncommon to see a human being near their house; for it was well known that her husband was a powerful giant, who would never eat anything but human flesh, if he could possibly get it; that he would walk fifty miles to procure it, usually being out the whole day for that purpose.
            """).strip()

        expected_output = textwrap.dedent("""
            Jack pursued his journey. █████████████████████████████████████████████████████████████████████████████████ A plain-looking woman was at the door: he accosted her, begging she would give him a morsel of bread and a night’s lodging. ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
            """).strip()

        concepts = ["house"]

        redacted_text, count = redact_concepts(input_text, concepts)
        self.assertEqual(redacted_text.strip(), expected_output)
        self.assertEqual(count, 2)  # Three sentences redacted




if __name__ == '__main__':
    unittest.main()