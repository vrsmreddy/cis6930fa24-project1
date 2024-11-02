import argparse
import spacy
import os
import glob
import sys
import re
import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
from nltk.corpus import wordnet as wn
import string

# Suppress specific FutureWarning from PyTorch
warnings.filterwarnings("ignore", category=FutureWarning, module="thinc")

# Download necessary NLTK data
nltk.download('wordnet')

# Initialize the sentence transformer model for better sentence embeddings
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load SpaCy model
nlp = spacy.load("en_core_web_md")

# Use a consistent block length regardless of the entity length
REDACTION_CHAR = "█"

def redact_text_with_char(text):
    return REDACTION_CHAR * len(text)

def redact_names(text):
    """
    Redacts personal names and email addresses from the text using spaCy's NER model and regex.
    Also redacts names in metadata fields.

    Parameters:
    - text (str): The input text to be redacted.

    Returns:
    - text (str): The redacted text.
    - count (int): The total number of redactions made.
    """
    doc = nlp(text)
    count = 0
    redactions = []

    # List of day abbreviations to exclude from redaction
    day_abbreviations = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}

    # Redact recognized PERSON entities
    for ent in doc.ents:
        if (
            ent.label_ == "PERSON"
            and len(ent.text) > 2  # Exclude short words
            and ent.text not in day_abbreviations  # Exclude day abbreviations
        ):
            redactions.append((ent.start_char, ent.end_char, redact_text_with_char(ent.text)))
            count += 1

    # Find email addresses using regex and add to redactions
    email_pattern = re.compile(
        r'\b[A-Za-z0-9._%+\'+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        re.IGNORECASE
    )
    for match in email_pattern.finditer(text):
        start, end = match.span()
        redactions.append((start, end, redact_text_with_char(match.group())))
        count += 1
    
    # Additional regex-based name redaction for common salutations
    salutation_pattern = re.compile(
        r'\b(Dear|Hello|Hi)\s+([A-Z][a-z]+)\b',
        re.IGNORECASE
    )
    for match in salutation_pattern.finditer(text):
        start, end = match.span(2)  # Redact only the name part
        redactions.append((start, end, redact_text_with_char(match.group(2))))
        count += 1

    # Apply all redactions in reverse order to avoid disrupting indices
    for start, end, replacement in sorted(redactions, key=lambda x: x[0], reverse=True):
        text = text[:start] + replacement + text[end:]

    # Redact names from metadata fields
    text, metadata_count = redact_metadata_fields(text)
    count += metadata_count

    return text, count

def redact_metadata_fields(text):
    count = 0

    def redact_folder_match(m):
        nonlocal count
        folder_path = m.group(2)
        # Split the folder path by backslashes
        folders = folder_path.split('\\')
        redacted_folders = []
        common_folders = {"Inbox", "Sent Items", "Drafts", "Trash", "Sent Mail"}
        for folder in folders:
            # If folder name contains digits or is a common folder, do not redact
            if any(char.isdigit() for char in folder) or folder.strip() in common_folders:
                redacted_folders.append(folder)
            else:
                # Redact the folder name
                redacted_folders.append(redact_text_with_char(folder))
                count += 1
        redacted_folder_path = '\\'.join(redacted_folders)
        return m.group(1) + redacted_folder_path

    def redact_match(m):
        nonlocal count
        redacted = m.group(1) + redact_text_with_char(m.group(2))
        count += 1
        if m.lastindex and m.lastindex >= 3:
            redacted += m.group(3)
        return redacted

    # Patterns and replacements
    patterns = [
        # Names with underscores after a backslash
        (r'(\\)([A-Za-z]+_[A-Za-z]+)', redact_match),
        # Names with commas after a backslash
        (r'(\\)([A-Za-z]+, [A-Za-z ]+)', redact_match),
        # X-Folder paths
        (r'(X-Folder: \\)([^\n]+)', redact_folder_match),
        (r'(X-Folder: )([^\n]+)', redact_folder_match),
        # X-Origin
        (r'(X-Origin: )([A-Za-z-]+)', redact_match),
        # Updated X-FileName pattern to redact only the name
        (r'(X-FileName: )([\w.-]+)([^\n\r]*)', redact_match),
        # Names in X-From, X-To, X-cc, X-bcc fields
        (r'(X-(?:From|To|cc|bcc):\s*)([^<\n]+?)(\s*(?:<|$))', redact_match),
    ]

    # Apply patterns
    for pattern, repl in patterns:
        metadata_pattern = re.compile(pattern, re.IGNORECASE)
        text = metadata_pattern.sub(repl, text)

    return text, count

def redact_dates(text):
    count = 0
    # First, use spaCy's NER to find dates
    doc = nlp(text)
    redactions = []

    # List of duration keywords to check for
    duration_keywords = [
        'day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years',
        'hour', 'hours', 'minute', 'minutes', 'second', 'seconds'
    ]

    for ent in doc.ents:
        if ent.label_ == "DATE":
            # Check if the entity contains any duration keywords
            if any(word in ent.text.lower() for word in duration_keywords):
                continue  # Skip durations
            redactions.append((ent.start_char, ent.end_char))
            count += 1

    # Apply NER-based redactions in reverse order
    for start, end in sorted(redactions, key=lambda x: x[0], reverse=True):
        text = text[:start] + redact_text_with_char(text[start:end]) + text[end:]

    # Regex patterns to match common date formats and days of the week
    date_patterns = [
        r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b',  # Abbreviated days of the week
        r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',  # Full day names
        r'\b[A-Za-z]{3}, \d{1,2} [A-Za-z]+ \d{4}\b',  # "Dec, 13 December 2000"
        r'\b\d{1,2} [A-Za-z]+ \d{4}\b',  # "14 December 2000", "2 Feb 2002"
        r'\b-?\d{1,2}/\d{1,2}/\d{2,4}\b',  # "-12/29/00", "12/29/2000"
        r'\b-?\d{4}-\d{2}-\d{2}\b',  # "-2000-12-29", "2000-12-29"
        r'\b-?\d{1,2}-\d{1,2}-\d{2,4}\b',  # "-12-29-00", "12-29-2000"
        r'\b[A-Za-z]{3,9} \d{1,2}, \d{4}\b',  # "December 29, 2000"
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # "12/29/00", "12-29-2000"
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # "2000/12/29", "2000-12-29"
    ]

    # Apply each pattern to the text and redact
    for pattern in date_patterns:
        redacted_text, regex_count = re.subn(pattern, lambda x: redact_text_with_char(x.group()), text)
        if regex_count > 0:
            count += regex_count
            text = redacted_text

    # Specific pattern to match "MonthYear" in "X-Folder" (e.g., "Dec2000")
    x_folder_pattern = r'(X-Folder: .*?\\[A-Za-z]+_\w+_)(\w{3}\d{4})'
    text, x_folder_count = re.subn(
        x_folder_pattern,
        lambda x: x.group(1) + redact_text_with_char(x.group(2)),
        text
    )
    count += x_folder_count

    return text, count

def redact_phones(text):
    # Refined regex for standard U.S. phone numbers, excluding international numbers
    phone_pattern = re.compile(
        r'(?<!\w)'  # Ensure the phone number is not part of a word
        r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'  # Match phone numbers like (123) 456-7890, 123-456-7890
        r'(?!\w)'  # Ensure the phone number does not continue into another word
    )
    redacted_text, count = phone_pattern.subn(lambda x: redact_text_with_char(x.group()), text)
    return redacted_text, count

def redact_addresses(text):
    count = 0

    # Regular expressions for street addresses, city/state/ZIP, and floor numbers
    address_patterns = [
        # Matches street addresses (e.g., "123 Main Street", "260 Franklin Street, 19th Floor")
        re.compile(
            r'^\s*(\d{1,5}\s(?:[A-Z][a-z]+\s){0,4}'
            r'(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|'
            r'Lane|Ln|Way|Court|Ct|Circle|Cir|Place|Pl|Square|Sq|Loop|Broadway)'
            r'(?:,\s?\d{1,3}(?:st|nd|rd|th)\s(?:Floor|Fl))?)',
            re.IGNORECASE | re.MULTILINE
        ),
        # Matches city, state abbreviation, and ZIP code on a line (e.g., "Springfield, IL 62704")
        re.compile(
            r'^\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s?'
            r'(?:AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|'
            r'IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|'
            r'MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|'
            r'SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)\s?\d{5}(?:-\d{4})?)',
            re.IGNORECASE | re.MULTILINE
        ),
        # Matches floor numbers on a line (e.g., "5th Floor")
        re.compile(
            r'^\s*(\d{1,3}(?:st|nd|rd|th)\s(?:Floor|Fl))',
            re.IGNORECASE | re.MULTILINE
        ),
    ]
    # Collect spans to redact
    redaction_spans = []

    for pattern in address_patterns:
        for match in pattern.finditer(text):
            start, end = match.start(1), match.end(1)
            redaction_spans.append((start, end))

    # Remove overlapping spans
    redaction_spans = sorted(redaction_spans, key=lambda x: x[0])
    merged_spans = []
    for start, end in redaction_spans:
        if merged_spans and start <= merged_spans[-1][1]:
            merged_spans[-1] = (merged_spans[-1][0], max(merged_spans[-1][1], end))
        else:
            merged_spans.append((start, end))

    # Redact the text using the spans
    redacted_text = []
    last_idx = 0
    for start, end in merged_spans:
        redacted_text.append(text[last_idx:start])
        redacted_text.append(redact_text_with_char(text[start:end]))
        last_idx = end
        count += 1
    redacted_text.append(text[last_idx:])
    redacted_text = ''.join(redacted_text)

    return redacted_text, count

def get_synonyms(word):
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_', ' '))
    return synonyms

def redact_concepts(text, concepts, similarity_threshold=0.6):
    """
    Redacts entire sentences containing given concepts or similar terms based on word similarity.

    Parameters:
    - text (str): The input text to be redacted.
    - concepts (list of str): The concepts to look for and redact related sentences.
    - similarity_threshold (float): The threshold for determining if a word should trigger redaction.

    Returns:
    - Tuple[str, int]: The redacted text and the count of sentences redacted.
    """
    # Get synonyms for each concept
    synonyms = {concept: get_synonyms(concept) for concept in concepts}

    # Process the text with spaCy to get sentences
    doc = nlp(text)
    redacted_text = text
    redacted_count = 0  # Counter for redacted sentences

    for sent in doc.sents:
        # Flag to determine if the sentence should be redacted
        redact_sentence = False

        # Get the text of the sentence
        sent_text = sent.text

        # Remove leading and trailing whitespace for processing
        cleaned_text = sent_text.strip()

        # Split the cleaned sentence into words for individual comparison
        words = [token.text for token in nlp(cleaned_text)]

        for concept, syn_set in synonyms.items():
            # Generate embedding for the concept
            concept_embedding = sentence_model.encode(concept, convert_to_tensor=True)

            for word in words:
                # Skip stop words and punctuation
                if word.lower() in nlp.Defaults.stop_words or word in string.punctuation:
                    continue

                # Generate embedding for the current word
                word_embedding = sentence_model.encode(word, convert_to_tensor=True)

                # Check similarity for the concept word itself
                word_similarity = cosine_similarity(
                    [word_embedding.cpu().numpy()], [concept_embedding.cpu().numpy()]
                )

                # If similarity is high, mark the sentence for redaction
                if word_similarity[0][0] > similarity_threshold:
                    redact_sentence = True
                    break

                # Check for synonyms within the cleaned sentence text
                for synonym in syn_set:
                    synonym_embedding = sentence_model.encode(synonym, convert_to_tensor=True)
                    synonym_similarity = cosine_similarity(
                        [word_embedding.cpu().numpy()], [synonym_embedding.cpu().numpy()]
                    )

                    if synonym_similarity[0][0] > similarity_threshold:
                        redact_sentence = True
                        break

                if redact_sentence:
                    break

            if redact_sentence:
                break

        # If the sentence should be redacted
        if redact_sentence:
            # Increment the redacted sentence count
            redacted_count += 1
            # Replace the sentence in the redacted text
            # Use the original sentence to preserve formatting
            redacted_sentence = ''.join(
                '\n' if char == '\n' else REDACTION_CHAR for char in sent_text
            )
            # Ensure we replace the exact sentence only once
            redacted_text = redacted_text.replace(sent_text, redacted_sentence, 1)

    return redacted_text, redacted_count


def redact_entities(text, args):
    total_counts = {"names": 0, "dates": 0, "phones": 0, "addresses": 0, "concepts": 0}

    if args.names:
        text, count = redact_names( text)
        total_counts["names"] += count
    if args.dates:
        text, count = redact_dates(text)
        total_counts["dates"] += count
    if args.phones:
        text, count = redact_phones(text)
        total_counts["phones"] += count
    if args.address:
        text, count = redact_addresses(text)
        total_counts["addresses"] += count
    if args.concept:
        text, count = redact_concepts(text, args.concept)
        total_counts["concepts"] += count  # Update with actual redaction count

    return text, total_counts


def main():
    parser = argparse.ArgumentParser(description='Redact sensitive information from text files.')
    parser.add_argument('--input', type=str, help='Glob for input text files', required=True)
    parser.add_argument('--output', type=str, help='Directory to save censored files', required=True)
    parser.add_argument('--names', action='store_true', help='Censor names')
    parser.add_argument('--dates', action='store_true', help='Censor dates')
    parser.add_argument('--phones', action='store_true', help='Censor phone numbers')
    parser.add_argument('--address', action='store_true', help='Censor addresses')
    parser.add_argument('--concept', action='append', help='Censor specific concepts', required=False)
    parser.add_argument('--stats', type=str, help='Output statistics to a file or stderr/stdout', default='stdout')
    args = parser.parse_args()

    input_files = glob.glob(args.input, recursive=True)
    if not input_files:
        print(f"No files matched the input pattern: {args.input}")
        return

    for file_path in input_files:
        if os.path.isfile(file_path):
            print(f"Processing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            redacted_content, total_counts = redact_entities(content, args)
            output_dir = os.path.abspath(args.output)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, os.path.basename(file_path) + ".censored")
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(redacted_content)
            print(f"File written to: {output_path}")
            stats = f"File: {file_path}\nRedacted Entities:\n"
            for key, count in total_counts.items():
                stats += f"- {key.capitalize()}: {count}\n"
            write_stats(stats, args.stats)
        else:
            print(f"Skipping non-file item: {file_path}")

def write_stats(stats, output_path):
    if output_path == 'stderr':
        sys.stderr.write(stats)
    elif output_path == 'stdout':
        sys.stdout.write(stats)
    else:
        with open(output_path, 'w') as f:
            f.write(stats)

if __name__ == "__main__":
    main()
