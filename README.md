# README.md

## CIS 6930, Fall 2024 Project 1: The Redactor

### Author
Rama Satyanarayana Murthy Reddy Velagala (r.velagala@ufl.edu)

### Introduction
The Redactor is a Python program designed to censor sensitive information in text documents, including names, dates, phone numbers, addresses, and custom concepts. This tool was created as part of CIS 6930, Fall 2024 to demonstrate the use of data processing pipelines and text redaction, leveraging natural language processing (NLP) capabilities to ensure privacy in shared documents.

The redactor is implemented using Python with NLP support from SpaCy, NLTK, and Sentence Transformers. The user can specify types of sensitive information to redact using command-line arguments, which makes the tool flexible and easy to use.

### How to Install and Run

1. **Dependencies**
   - Python 3.12
   - [Pipenv](https://pipenv.pypa.io/en/latest/)

   Install required packages using `pipenv`:
   ```sh
   pipenv install
   ```

   The Pipfile includes the necessary dependencies such as:
   - `spacy`
   - `nltk`
   - `sentence-transformers`
   - `scikit-learn`
   - `transformers`
   - `torch`
   - `pytest` for testing

   Example content of `Pipfile`:
   ```toml
   [[source]]
   url = "https://pypi.org/simple"
   verify_ssl = true
   name = "pypi"

   [packages]
   spacy = "*"
   nltk = "*"
   sentence-transformers = "*"
   scikit-learn = "*"
   transformers = "*"
   torch = "*"

   en-core-web-md = {file = "https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl"}

   [dev-packages]

   [requires]
   python_version = "3.12"
   python_full_version = "3.12.5"
   ```

2. **Download and Install SpaCy Model**
   ```sh
   pipenv run python -m spacy download en_core_web_md
   ```

3. **Running the Redactor**
   The following command demonstrates how to run the program with various redaction flags:
   ```sh
   pipenv run python redactor.py --input '*.txt' \
                               --names --dates --phones --address \
                               --concept 'kids' \
                               --output 'files/' \
                               --stats stderr
   ```

### Parameters

- **--input**: Takes a glob pattern representing the files to be processed. Supports multiple inputs.

  ```sh
   pipenv run python redactor.py --input '*.txt' \
                               --names --dates --phones --address \
                               --concept 'kids' \
                               --output 'files/' \
                               --stats stderr
   ```

- **--output**: Specifies the directory where censored files will be stored. The files are saved with the `.censored` extension.
- **Censor Flags**:
  - `--names`: Redacts names (detected using SpaCy's named entity recognition).
  - `--dates`: Redacts written dates in various formats (e.g., 4/9/2025, April 9th, etc.).
  - `--phones`: Redacts phone numbers in standard U.S. formats.
  - `--address`: Redacts physical addresses (excluding email addresses).
- **--concept**: Accepts a word or phrase representing a concept. The program redacts any sentence containing the concept or its synonyms. For example, if `--concept 'kids'` is provided, sentences containing words like "children" or "minors" will also be redacted.
- **--stats**: Specifies where to output redaction statistics. Supports output to `stderr`, `stdout`, or a specified file.

### Concept Definition and Methodology
A concept in this project is defined as an idea or theme represented by a word or phrase. For example, the concept of "prison" also encompasses words such as "jail" or "incarcerated." Redaction of concepts involves using semantic similarity to identify related terms.

To determine the context of a concept, the system uses the SentenceTransformer model `all-MiniLM-L6-v2` to compute embeddings and cosine similarity between words and the given concept. Synonyms are also fetched using WordNet, and sentences with similar words are redacted if they exceed a defined similarity threshold.

### Stats Output
The `--stats` flag provides a summary of the redaction process. The summary includes:
- The types of entities redacted (e.g., names, dates, phones, addresses, concepts).
- The count of each entity type redacted.


Example stats format:
```
File: example.txt
Redacted Entities:
- Names: 5
- Dates: 3
- Phones: 2
- Addresses: 4
- Concepts: 6
```

Here I'm Providing  detailed descriptions of the functions used in the redaction tool code. Each function is designed to handle a specific aspect of text redaction, such as redacting names, dates, phone numbers, addresses, or concepts. The code utilizes natural language processing libraries like SpaCy, NLTK, and Sentence Transformers to identify and censor sensitive information.

### 1. `redact_text_with_char(text)`
- **Purpose**: Replaces every character in the input text with a redaction character (`█`).
- **Parameters**: `text` (str) - The text to be redacted.
- **Returns**: A string of redacted characters.

### 2. `redact_names(text)`
- **Purpose**: Redacts personal names and email addresses using SpaCy NER and regex.
- **Parameters**: `text` (str) - The text to be redacted.
- **Returns**: Tuple of redacted text and count of redactions.
- **Patterns Used**:
  - **NER Detection**: SpaCy model for `PERSON` entities.
  - **Email Regex**: `r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'` to redact email addresses.

### 3. `redact_metadata_fields(text)`
- **Purpose**: Handles redaction of metadata such as folder names, email headers (`X-From`, `X-To`, `X-Origin`).
- **Parameters**: `text` (str) - The input text.
- **Returns**: Tuple of redacted text and count of redactions.
- **Patterns Used**:
  - **Folder Path**: Redacts folder names after backslashes.
  - **Headers**: Matches patterns like `X-Folder`, `X-Origin`, `X-FileName`.

Here I'm proving an explanation of the function used to redact personal names, email addresses, and metadata information from text in the redaction tool. The `redact_names` and `redact_metadata_fields` functions work together to remove sensitive information that pertains to names and metadata, ensuring confidentiality.

### Function: `redact_names(text)`
The `redact_names` function is responsible for identifying and redacting personal names and email addresses from the provided text. It uses SpaCy's Named Entity Recognition (NER) model to detect names and a regular expression to detect email addresses. Additionally, it handles redaction of specific names from metadata fields.

#### Parameters
- **`text`** (str): The input text to be redacted for names and email addresses.

#### Returns
- **Tuple**: The function returns two elements:
  - **`redacted_text`** (str): The text after redacting names, email addresses, and metadata fields.
  - **`count`** (int): The total count of redactions made in the text.

### Function Logic
1. **NER-Based Name Redaction**
   - The function uses SpaCy's NER model to detect entities labeled as `PERSON`, indicating personal names.
   - **Exclusion of Day Abbreviations**: Short words like day abbreviations (e.g., "Mon," "Tue") are excluded to avoid incorrect redactions.
   - **Redaction**: Names longer than two characters that are detected by the NER model are redacted using the `redact_text_with_char` function, which replaces the text with a block character (`█`).

2. **Regex-Based Email Redaction**
   - The function uses a regular expression to find email addresses in the text and adds them to the redaction list.
   - **Pattern Used**:
     ```python
     r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
     ```
   - **Purpose**: Matches common email address formats, such as "john.doe@example.com."

3. **Applying Redactions**
   - To avoid disrupting text indices during multiple replacements, all redactions are applied in reverse order.

4. **Metadata Fields Redaction**
   - The function calls `redact_metadata_fields` to handle redaction of names in specific metadata fields, which may contain sensitive information such as folder paths, origin information, or names in email headers.

### Function: `redact_metadata_fields(text)`
The `redact_metadata_fields` function is responsible for redacting names and other sensitive information present in metadata fields. These metadata fields often contain information like folder paths, file names, and email headers, which could contain personal identifiers.

#### Parameters
- **`text`** (str): The input text that contains metadata fields to be redacted.

#### Returns
- **Tuple**: The function returns two elements:
  - **`redacted_text`** (str): The text after redacting metadata fields.
  - **`count`** (int): The total count of redactions made in the metadata fields.

### Metadata Patterns
The function uses several regular expressions to detect and redact sensitive information from metadata fields. Below are the patterns used:

1. **Folder Path Names**
   - **Pattern**:
     ```python
     r'(\\)([A-Za-z]+_[A-Za-z]+)'
     ```
   - **Purpose**: Matches folder names containing underscores after a backslash (e.g., "\Doe_John").
   - **Logic**: Folder names that do not contain digits or are not common folders (e.g., "Inbox," "Sent Items") are redacted.

2. **Comma-Separated Names in Folder Paths**
   - **Pattern**:
     ```python
     r'(\\)([A-Za-z]+, [A-Za-z ]+)'
     ```
   - **Purpose**: Matches folder names with commas after a backslash (e.g., "\Doe, John").

3. **X-Folder Paths**
   - **Pattern**:
     ```python
     r'(X-Folder: \\)([^\n]+)'
     ```
   - **Purpose**: Matches folder paths in "X-Folder" metadata fields.

4. **X-Origin**
   - **Pattern**:
     ```python
     r'(X-Origin: )([A-Za-z-]+)'
     ```
   - **Purpose**: Matches origin information (e.g., "X-Origin: Doe-J").

5. **X-FileName**
   - **Pattern**:
     ```python
     r'(X-FileName: )([\w.-]+)([^\n\r]*)'
     ```
   - **Purpose**: Matches file names in "X-FileName" metadata fields while preserving non-sensitive information.

6. **Email Header Fields (X-From, X-To, X-cc, X-bcc)**
   - **Pattern**:
     ```python
     r'(X-(?:From|To|cc|bcc):\s*)([^<\n]+?)(\s*(?:<|$))'
     ```
   - **Purpose**: Matches names in email headers like "X-From" or "X-To."

### Applying Patterns
- Each pattern is applied to the text using the `sub()` method from the `re` module, which replaces matched metadata fields with redacted text.
- **Count Tracking**: The `count` variable is used to track the total number of redactions made.

### Example
Suppose the input text contains the following:
```
X-From: Jane Doe
X-To: jdoe <john.doe@example.com>
X-Origin: Doe-J
X-Folder: \Doe_John\Inbox
```
The `redact_names` and `redact_metadata_fields` functions will:
1. Redact "Jane Doe" and "john.doe@example.com" in the email fields.
2. Redact "Doe-J" in the origin metadata.
3. Redact "Doe_John" in the folder path.

The output would look like this:
```
X-From: ████████
X-To: ████ <████████████████████>
X-Origin: █████
X-Folder: \████████\Inbox
```

### Summary
The `redact_names` and `redact_metadata_fields` functions effectively redact personal names, email addresses, and metadata fields by:
- Utilizing SpaCy's NER model to identify personal names in the text.
- Using regular expressions to find and redact email addresses and metadata containing sensitive information.
- Maintaining the original structure of the text while ensuring that all sensitive information is completely removed.

### 4. `redact_dates(text)`
- **Purpose**: Redacts dates using SpaCy NER and regex patterns for various date formats.
- **Parameters**: `text` (str) - The text to be redacted.
- **Returns**: Tuple of redacted text and count of redacted dates.
- **Patterns Used**:
  - **NER Detection**: SpaCy for `DATE` entities.
  - **Regex Patterns**:
    - Days of the week: `r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b'`
    - ISO Dates: `r'\b\d{4}-\d{2}-\d{2}\b'`
    - Written Dates: `r'\b\d{1,2} [A-Za-z]+ \d{4}\b'`

Here I'm Providing an explanation of the function used to redact dates from text in the redaction tool. The `redact_dates` function is designed to identify and redact various types of dates, including natural language expressions, standard date formats, and specific mentions of days of the week. The function combines the power of SpaCy's Named Entity Recognition (NER) model and regular expressions to detect and redact dates.

### Function: `redact_dates(text)`
The `redact_dates` function is responsible for identifying and redacting all date-related information from the provided text. This includes removing specific calendar dates while preserving durations such as "3 days" or "2 weeks." The function leverages SpaCy's NER model and regular expressions to find various forms of date expressions.

#### Parameters
- **`text`** (str): The input text that needs to be redacted for date information.

#### Returns
- **Tuple**: The function returns two elements:
  - **`redacted_text`** (str): The text after the redaction of date information.
  - **`count`** (int): The total count of redactions made in the text.

### Function Logic
1. **NER-Based Date Redaction**
   - The function uses SpaCy's NER model to identify entities labeled as `DATE`. This helps to locate and redact phrases that represent dates, such as "July 4th" or "March 2020."
   - **Duration Filtering**: To avoid redacting durations (e.g., "5 days" or "3 weeks"), the function checks if the date entity contains duration-related keywords. If such keywords are found, the entity is skipped.
   - **Redaction**: Identified dates are collected and redacted using a custom function (`redact_text_with_char`) to replace the original text with the redaction character (`█`).

2. **Regex-Based Date Redaction**
   - After the initial NER-based redaction, the function applies several regex patterns to capture and redact dates that might not have been detected by SpaCy. Below are the different patterns used:
     - **Days of the Week (Abbreviated and Full)**:
       - `\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b` matches abbreviated day names.
       - `\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b` matches full day names.
     - **Common Date Formats**:
       - `\b[A-Za-z]{3}, \d{1,2} [A-Za-z]+ \d{4}\b`: Matches formats like "Dec, 13 December 2000."
       - `\b\d{1,2} [A-Za-z]+ \d{4}\b`: Matches formats like "14 December 2000" or "2 Feb 2002."
       - `\b-?\d{1,2}/\d{1,2}/\d{2,4}\b`: Matches formats like "12/29/2000" or "-12/29/00."
       - `\b\d{4}-\d{2}-\d{2}\b`: Matches formats like "2000-12-29."
       - `\b\d{1,2}-\d{1,2}-\d{2,4}\b`: Matches formats like "12-29-2000."
       - `\b[A-Za-z]{3,9} \d{1,2}, \d{4}\b`: Matches formats like "December 29, 2000."
       - `\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b`: Matches formats like "12/29/00" or "12-29-2000."
       - `\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b`: Matches formats like "2000/12/29" or "2000-12-29."
   - **Applying Patterns**: Each regex pattern is applied to the text, and the matched dates are replaced with the redaction character using the `subn()` function from the `re` module, which also returns the count of replacements.

3. **Handling Specific Metadata**
   - **X-Folder Pattern**: The function includes a specific regex pattern to redact dates present in metadata fields like "X-Folder" (e.g., "Dec2000").
   - **Pattern Used**: `r'(X-Folder: .*?\\[A-Za-z]+_\w+_)(\w{3}\d{4})'` captures date strings in folder metadata, and replaces them with the redaction character.

### Example
Suppose the input text contains the following:
```
The meeting is scheduled on Monday, 14 May 2020. Please refer to the X-Folder: \Archives_2020\May2020.
```
The `redact_dates` function will:
1. Identify "Monday" and "14 May 2020" as dates and redact them.
2. Identify "May2020" in the metadata field and redact it.

The output would look like this:
```
The meeting is scheduled on ██████, ██████████. Please refer to the X-Folder: \Archives_2020\███████.
```

### Summary
The `redact_dates` function effectively redacts date-related information by:
- Leveraging SpaCy's NER model to capture natural language expressions representing dates.
- Using well-crafted regular expressions to identify and redact various common date formats that may not be captured by NER.
- Maintaining the original structure of the text while ensuring that all sensitive date information is completely removed.

### 5. `redact_phones(text)`
- **Purpose**: Redacts phone numbers in various standard formats.
- **Parameters**: `text` (str) - The text to be redacted.
- **Returns**: Tuple of redacted text and count of redacted phone numbers.
- **Pattern Used**: `r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'` for U.S. phone numbers.
Here I'M Providing an explanation of the function used to redact phone numbers from text in the redaction tool. The `redact_phones` function is designed to identify and redact phone numbers that are written in standard U.S. formats using regular expressions. Below, the function is explained in detail, including its purpose and the regular expression used.

### Function: `redact_phones(text)`
The `redact_phones` function is responsible for identifying and redacting phone numbers from the provided text. The function targets typical phone number formats, including numbers written with parentheses, dashes, or spaces.

#### Parameters
- **`text`** (str): The input text that contains phone numbers to be redacted.

#### Returns
- **Tuple**: The function returns two elements:
  - **`redacted_text`** (str): The text after the redaction of phone numbers.
  - **`count`** (int): The total count of redactions made in the text.

### Phone Number Pattern
The function uses a regular expression to detect phone numbers in the text. Below is a detailed explanation of the pattern used:

- **Pattern**:
  ```python
  r'(?<!\w)(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})(?!\w)'
  ```
- **Purpose**: Matches standard U.S. phone numbers, such as:
  - "(123) 456-7890"
  - "123-456-7890"
  - "123.456.7890"
  - "123 456 7890"
- **Explanation**:
  - `(?<!\w)`: Ensures the phone number is not part of a larger word.
  - `\(?\d{3}\)?`: Matches an optional area code enclosed in parentheses (e.g., "(123)").
  - `[-.\s]?`: Matches an optional separator (dash, dot, or space).
  - `\d{3}`: Matches the next three digits.
  - `[-.\s]?`: Matches another optional separator.
  - `\d{4}`: Matches the final four digits of the phone number.
  - `(?!\w)`: Ensures the phone number is not followed by a word character.
- **Flags**: No specific flags are used since the regex is already case-insensitive by nature and matches standard formats.

### Function Logic
1. **Redacting Phone Numbers**
   - The function uses the `subn()` method from the `re` module to find and replace all instances of the phone number pattern in the text. Each detected phone number is replaced with the redaction character (`█`), maintaining the original length of the number.
   - The `count` variable is used to track the number of phone numbers redacted.

2. **Returning Results**
   - The function returns the redacted version of the text and the total count of redactions performed.

### Example
Suppose the input text contains the following:
```
Call me at (123) 456-7890 or at 987-654-3210.
```
The `redact_phones` function will:
1. Identify "(123) 456-7890" and "987-654-3210" as phone numbers.
2. Replace both instances with the redaction character `█` to ensure sensitive phone information is not visible:
```
Call me at ███████████ or at ██████████.
```

### Summary
The `redact_phones` function effectively redacts phone number information by:
- Using a well-crafted regular expression to match different phone number formats commonly used in the U.S.
- Maintaining the original structure of the text while ensuring that sensitive phone number information is completely removed.


### 6. `redact_addresses(text)`
- **Purpose**: Redacts physical addresses, including street addresses and city/state/ZIP combinations.
- **Parameters**: `text` (str) - The text to be redacted.
- **Returns**: Tuple of redacted text and count of redacted addresses.
- **Patterns Used**:
  - **Street Address**: `r'^\s*(\d{1,5}\s(?:[A-Z][a-z]+\s){0,4}(?:Street|St|Avenue|Ave|...))'`
  - **City/State/ZIP**: Matches city names with state abbreviations and ZIP codes.
Address Redaction in The Redactor

Here I'm Providing  an explanation of the function used to redact addresses from text in the redaction tool. The `redact_addresses` function is designed to identify and redact various types of addresses, such as street addresses, city/state/ZIP combinations, and floor numbers, using regular expressions. Below, each part of the code is explained in detail, including the purpose of different regular expressions used.

### Function: `redact_addresses(text)`
The `redact_addresses` function is responsible for identifying and redacting all address-related information from the provided text. This includes common address components like street addresses, city and state abbreviations, ZIP codes, and floor numbers.

#### Parameters
- **`text`** (str): The input text that needs to be redacted for address information.

#### Returns
- **Tuple**: The function returns two elements:
  - **`redacted_text`** (str): The text after the redaction of address information.
  - **`count`** (int): The total count of redactions made in the text.

### Address Patterns
The function uses several regular expressions to detect different types of address patterns in the text. Below is a detailed explanation of each pattern used:

1. **Street Address Pattern**
   - **Pattern**:
     ```python
     r'^\s*(\d{1,5}\s(?:[A-Z][a-z]+\s){0,4}(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct|Circle|Cir|Place|Pl|Square|Sq|Loop|Broadway)(?:,\s?\d{1,3}(?:st|nd|rd|th)\s(?:Floor|Fl))?)'
     ```
   - **Purpose**: Matches common street addresses, such as "123 Main Street" or "260 Franklin Street, 19th Floor." The pattern accounts for:
     - A leading number (1-5 digits) for the house number.
     - A series of capitalized words that represent the street name.
     - Common street suffixes like "Street," "Avenue," "Boulevard," etc.
     - Optional floor numbers (e.g., "5th Floor").
   - **Flags**: `re.IGNORECASE` and `re.MULTILINE` are used to ensure that the search is case-insensitive and spans multiple lines.

2. **City/State/ZIP Pattern**
   - **Pattern**:
     ```python
     r'^\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s?(?:AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)\s?\d{5}(?:-\d{4})?)'
     ```
   - **Purpose**: Matches city names followed by state abbreviations and ZIP codes, such as "Springfield, IL 62704."
     - Allows for multiple words in the city name.
     - Recognizes standard two-letter U.S. state abbreviations.
     - Matches 5-digit ZIP codes, optionally followed by a 4-digit extension.
   - **Flags**: `re.IGNORECASE` and `re.MULTILINE` are used to allow case-insensitive matching across multiple lines.

3. **Floor Number Pattern**
   - **Pattern**:
     ```python
     r'^\s*(\d{1,3}(?:st|nd|rd|th)\s(?:Floor|Fl))'
     ```
   - **Purpose**: Matches floor numbers, such as "5th Floor."
     - Detects floor numbers with suffixes like "st," "nd," "rd," "th" followed by "Floor" or "Fl."
   - **Flags**: `re.IGNORECASE` and `re.MULTILINE` ensure case-insensitive matching and span multiple lines.

### Function Logic
1. **Collecting Spans for Redaction**
   - The function iterates over each pattern and uses the `finditer()` method to locate matches within the text. For each match, the start and end positions are recorded to create a list of spans that need to be redacted.

2. **Handling Overlapping Spans**
   - The spans are sorted based on their starting position, and overlapping spans are merged. This ensures that the final redaction process does not contain overlapping or redundant redactions, which could otherwise lead to incorrect replacements.

3. **Redacting the Text**
   - The text is redacted based on the merged spans. For each span, the text between the start and end positions is replaced with the redaction character (`█`), which maintains the length of the redacted content.
   - The `count` variable is updated to track the number of redactions performed.

### Example
Suppose the input text contains the following:
```
123 Main Street, 5th Floor
Springfield, IL 62704
```
The `redact_addresses` function will:
1. Identify "123 Main Street, 5th Floor" as a street address and "Springfield, IL 62704" as a city/state/ZIP.
2. Replace both instances with the redaction character `█` to ensure sensitive address information is not visible.

### Summary
The `redact_addresses` function effectively redacts address information by:
- Using a series of well-crafted regular expressions to match different types of address-related data.
- Handling overlapping spans to ensure consistent and accurate redaction.
- Maintaining the original structure of the text while ensuring that sensitive address information is completely removed.

### 7. `get_synonyms(word)`
- **Purpose**: Fetches synonyms for a given word using NLTK WordNet to expand concept coverage.
- **Parameters**: `word` (str) - The word to find synonyms for.
- **Returns**: Set of synonyms.

### 8. `redact_concepts(text, concepts, similarity_threshold=0.6)`
- **Purpose**: Redacts sentences containing given concepts or similar terms using Sentence Transformers.
- **Parameters**:
  - `text` (str) - The input text.
  - `concepts` (list of str) - Concepts to redact.
  - `similarity_threshold` (float) - The threshold for similarity to trigger redaction.
- **Returns**: Tuple of redacted text and count of sentences redacted.
Concept Redaction in The Redactor

### Concept Definition
A **concept** in the context of this redaction tool is defined as an abstract idea or theme represented by a specific word or phrase. It could be a topic or a general category, such as "prison," "money," or "children." Concepts can be directly mentioned or implied through synonymous terms. Therefore, the process of identifying concepts is not just about finding an exact match for a word, but also identifying related terms that represent the same idea.

### Creating the Context for a Concept
The context for a concept is created by identifying the concept itself as well as its synonyms and semantically related words. To accomplish this, we use the following approach:

1. **Synonym Extraction**: We use NLTK's WordNet to gather synonyms for each provided concept. For instance, if the concept is "prison," the related terms like "jail," "incarceration," and "penitentiary" are also considered part of the concept. This allows us to extend the coverage of the redaction and ensure that semantically similar terms are included.
   - **Function Used**: `get_synonyms(word)`
   - **Implementation**: The function iterates through WordNet synsets and extracts lemmas to find synonyms.

2. **Semantic Similarity**: In addition to synonyms, the tool also considers words that may not be direct synonyms but are closely related based on context. We use Sentence Transformers to calculate semantic similarity between the words in the text and the provided concepts. This allows us to detect contextually related terms even if they are not exact matches.
   - **Embedding Generation**: Each word and concept is converted to an embedding using Sentence Transformers (`all-MiniLM-L6-v2`), and the similarity is calculated using cosine similarity.
   - **Similarity Threshold**: A similarity threshold (default 0.6) is used to determine whether a word is close enough to the concept to trigger redaction. This threshold can be adjusted to control the strictness of the redaction.

### Redaction Methodology
The redaction of concepts is performed at the **sentence level**. If a sentence contains any word that is identified as related to the concept, either through synonym detection or semantic similarity, the entire sentence is redacted. This approach ensures that the context surrounding the concept is fully removed, preventing any potential inference of sensitive information.

- **Function Used**: `redact_concepts(text, concepts, similarity_threshold=0.6)`
- **Steps Involved**:
  1. **Extract Synonyms**: For each concept, synonyms are fetched using `get_synonyms()`.
  2. **Sentence Tokenization**: The input text is tokenized into sentences using SpaCy's NLP model.
  3. **Word Embedding and Similarity Calculation**:
     - For each word in a sentence, an embedding is generated.
     - The embedding is compared to the concept's embedding and its synonyms' embeddings.
     - If the similarity exceeds the threshold, the sentence is marked for redaction.
  4. **Sentence Redaction**: If a sentence is marked for redaction, each character is replaced by the redaction character (`█`) to maintain the original formatting.

### Justification of Method
- **Comprehensive Coverage**: By using both synonyms and semantic similarity, the tool ensures that all instances of a concept are identified, even if they are expressed in different ways. This makes the redaction process more robust and reduces the risk of missing sensitive information.
- **Sentence-Level Redaction**: Redacting entire sentences ensures that no contextual clues are left behind. Simply redacting individual words could allow a reader to infer the redacted information from the surrounding context, which is why a broader approach is taken.
- **Adjustable Sensitivity**: The use of a similarity threshold allows for flexibility in determining what should be redacted. A higher threshold can be used for more precise redaction, while a lower threshold can be used for more aggressive redaction.

### Example
Suppose the concept to be redacted is "prison." The following steps are taken:
1. **Synonym Extraction**: Extracted synonyms may include "jail," "penitentiary," and "incarceration."
2. **Sentence Tokenization**: The text is split into sentences.
3. **Similarity Calculation**: Each word in a sentence is compared to the concept and its synonyms using cosine similarity.
4. **Redaction**: If a word like "jail" is found with a similarity score above the threshold, the entire sentence containing that word is redacted.

### Summary
The concept redaction method in The Redactor is designed to identify and censor sensitive themes by analyzing both direct synonyms and contextually related words. By leveraging NLP tools such as NLTK WordNet and Sentence Transformers, the tool effectively removes all references to a concept, ensuring that no sensitive information can be inferred from the text.

### 9. `redact_entities(text, args)`
- **Purpose**: Redacts multiple entity types based on provided arguments, including names, dates, phones, addresses, and concepts.
- **Parameters**:
  - `text` (str) - The text to be redacted.
  - `args` - Command-line arguments specifying which entities to redact.
- **Returns**: Tuple of redacted text and a dictionary of redaction counts.

### 10. `main()`
- **Purpose**: Handles command-line arguments, processes files, and invokes redaction functions.
- **Usage**: Reads input files, applies redaction as per the flags, and writes output files and statistics.

### 11. `write_stats(stats, output_path)`
- **Purpose**: Writes statistics regarding the redaction process to a specified destination.
- **Parameters**:
  - `stats` (str) - Statistics information.
  - `output_path` (str) - Destination to write the stats (`stderr`, `stdout`, or a file path).

Here I'm providing a detailed description of the output file format and how the statistics generated by the redactor tool are handled. The tool supports multiple output options for the statistics, including writing to a specified file, to standard output (`stdout`), or to standard error (`stderr`). The `write_stats` function is responsible for correctly implementing this behavior.

### Output File Format
The output files generated by the redactor tool are created after applying redaction to the input text. The censored versions of the files are saved in the output directory specified by the user, with the `.censored` extension added to the original filename.

#### Example of Output File Naming
- **Input File**: `document.txt`
- **Redacted Output File**: `document.txt.censored`

The output file retains the original structure and formatting of the text, with sensitive information replaced by a consistent redaction character (`█`). The redacted content ensures that all sensitive data (such as names, dates, addresses, phone numbers, and other defined concepts) are properly removed while maintaining the readability of non-sensitive information.

### Statistics Output
The redactor tool provides a summary of the redaction process, including the types of entities redacted and their counts. This summary is useful for understanding what was removed from the text and for verifying the effectiveness of the redaction.

The `write_stats(stats, output_path)` function handles the output of statistics in three different ways, depending on the value provided for the `--stats` argument:

1. **File Output**
   - If you provide a file name as the argument for `--stats`, the function writes the statistics summary to that file.
   - **Example**:
     ```
     --stats 'redaction_summary.txt'
     ```
     The summary will be saved to `redaction_summary.txt` in the current directory.

2. **stderr Output**
   - If you specify `stderr` as the value for `--stats`, the function writes the statistics summary to the standard error stream.
   - This is useful for logging purposes, especially in command-line environments where you want to separate the redaction process output from other output messages.
   - **Example**:
     ```
     --stats stderr
     ```
     The summary will be written to the standard error stream.

3. **stdout Output**
   - If you specify `stdout` as the value for `--stats`, the function writes the statistics summary to the standard output stream.
   - This is useful if you want to view the summary directly in the console or pipe the output to another command.
   - **Example**:
     ```
     --stats stdout
     ```
     The summary will be printed to the standard output stream.

### Example of Statistics Summary
The statistics summary provides details such as the file processed, the types of redactions performed, and the count of each type of redaction. Below is an example format for the statistics summary:
```
File: document.txt
Redacted Entities:
- Names: 5
- Dates: 3
- Phone Numbers: 2
- Addresses: 4
- Concepts: 1
```
The summary helps in verifying that the expected number of redactions has been made and allows users to track what types of sensitive information were present in the document.

### Implementation of `write_stats(stats, output_path)`
The `write_stats` function implements the behavior for handling the statistics output in all three cases:
- **File Output**: If `output_path` is a file name, the function opens the file in write mode and writes the statistics to it using standard file handling.
  ```python
  with open(output_path, 'w') as f:
      f.write(stats)
  ```
- **stderr Output**: If `output_path` is `'stderr'`, the function writes the statistics to the standard error stream using `sys.stderr.write(stats)`.
  ```python
  sys.stderr.write(stats)
  ```
- **stdout Output**: If `output_path` is `'stdout'`, the function writes the statistics to the standard output stream using `sys.stdout.write(stats)`.
  ```python
  sys.stdout.write(stats)
  ```

This implementation ensures flexibility, allowing users to choose the most suitable option for their use case.


### Libraries and Models Used
- **argparse**: Parses command-line arguments for redaction options.
- **SpaCy**: Detects names, dates, and other entities using a pre-trained NER model.
- **NLTK**: Uses WordNet to fetch synonyms for extending concept redaction.
- **Sentence Transformers**: Generates word embeddings for similarity comparison of concepts.
- **scikit-learn (cosine_similarity)**: Computes similarity between word embeddings.
- **Warnings**: Suppresses specific warnings from libraries.
- **Regex (re)**: Identifies and redacts patterns like phone numbers, addresses, and dates.




### Testing
Tests are implemented for each feature using `pytest`. Tests include redaction of names, dates, phone numbers, addresses, and concepts. To run the tests, use the following command:
```sh
pipenv run python -m pytest
```

**Test Files**:
- **`test_dates.py`**:

The `test_dates.py` file uses the `unittest` framework to verify the correctness of the `redact_dates` function. Below is a summary of the main test cases included:

1. **Day Name Redaction**
   - **Test Name**: `test_day_name`
   - **Purpose**: To verify that the function correctly redacts full day names (e.g., "Monday").
   - **Expected Output**: The day name is replaced by the redaction character (`█`), and the count of redactions is correctly updated.

2. **Duration Not Redacted**
   - **Test Name**: `test_duration`
   - **Purpose**: To ensure that durations (e.g., "3 weeks") are not mistakenly redacted, as they are not specific dates.
   - **Expected Output**: The duration remains intact, and the redaction count is zero.

3. **ISO Date Redaction**
   - **Test Name**: `test_iso_date`
   - **Purpose**: To verify that dates in ISO format (e.g., "2025-12-31") are correctly redacted.
   - **Expected Output**: The date is replaced by redaction characters, and the count is updated.

4. **Standard Date Format Redaction**
   - **Test Name**: `test_standard_date`
   - **Purpose**: To ensure that dates in standard formats (e.g., "12/25/2025") are correctly redacted.
   - **Expected Output**: The date is replaced by redaction characters, and the count is updated.

5. **Written Date Redaction**
   - **Test Name**: `test_written_date`
   - **Purpose**: To verify that written dates (e.g., "April 5th, 2020") are correctly redacted.
   - **Expected Output**: The date is replaced by redaction characters, and the count is updated.


- **`test_addresses.py`**:

The `test_addresses.py` file uses the `unittest` framework to verify the correctness of the `redact_addresses` function. Below is a summary of the main test cases included:

1. **Address in Signature Redaction**
   - **Test Name**: `test_address_in_signature`
   - **Purpose**: To verify that the function correctly redacts addresses found in the email signature (e.g., "123 Main Street, 5th Floor").
   - **Expected Output**: The address is replaced by the redaction character (`█`), and the count of redactions is correctly updated.

2. **Address in Body Redaction**
   - **Test Name**: `test_address_in_body`
   - **Purpose**: To ensure that addresses provided in the main body of the text (e.g., "456 Elm Street, Anytown, CA 90210") are correctly redacted.
   - **Expected Output**: The address is replaced by redaction characters, and the count is updated.

3. **No Address Present**
   - **Test Name**: `test_no_address`
   - **Purpose**: To verify that the function does not mistakenly redact text when no address is present.
   - **Expected Output**: The text remains unchanged, and the redaction count is zero.

- **`test_names.py`**:

The `test_names.py` file uses the `unittest` framework to verify the correctness of the `redact_names` function. Below is a summary of the main test cases included:

1. **Email Address Redaction**
   - **Test Name**: `test_email_redaction`
   - **Purpose**: To verify that the function correctly redacts email addresses from the text (e.g., "john.doe@example.com").
   - **Expected Output**: The email address is replaced by the redaction character (`█`), and the count of redactions is correctly updated.

2. **Metadata Field Redaction**
   - **Test Name**: `test_metadata_redaction`
   - **Purpose**: To ensure that personal names appearing in metadata fields (e.g., "X-From", "X-To", "X-Origin") are correctly redacted.
   - **Expected Output**: The names in the metadata fields are replaced by redaction characters, and the count is updated.

3. **Filename Metadata Redaction**
   - **Test Name**: `test_x_filename_redaction`
   - **Purpose**: To verify that personal names in file metadata (e.g., "X-FileName") are correctly redacted.
   - **Expected Output**: The filename is partially redacted to remove sensitive information, while other parts of the metadata remain intact.

4. **Folder Path Redaction**
   - **Test Name**: `test_x_folder_redaction`
   - **Purpose**: To ensure that personal names in folder paths (e.g., "X-Folder") are correctly redacted, while common folder names are preserved.
   - **Expected Output**: Only the sensitive parts of the folder paths are replaced by redaction characters, and the count is updated.

5. **Preservation of Non-Sensitive Dates**
   - **Test Name**: `test_date_preservation`
   - **Purpose**: To verify that non-sensitive dates (e.g., "Mon, 14 May 2001") appearing in metadata are not incorrectly redacted.
   - **Expected Output**: The date remains intact, and the redaction count remains unchanged.

- **`test_phones.py`**:

The `test_phones.py` file uses the `unittest` framework to verify the correctness of the `redact_phones` function. Below is a summary of the main test cases included:

1. **Standard Phone Number Redaction**
   - **Test Name**: `test_standard_phone`
   - **Purpose**: To verify that phone numbers formatted with parentheses (e.g., "(123) 456-7890") are correctly redacted.
   - **Expected Output**: The phone number is replaced by the redaction character (`█`), and the count of redactions is correctly updated.

2. **Dashed Phone Number Redaction**
   - **Test Name**: `test_dashed_phone`
   - **Purpose**: To ensure that phone numbers using dashes as separators (e.g., "123-456-7890") are correctly redacted.
   - **Expected Output**: The phone number is replaced by redaction characters, and the count is updated.

3. **Dotted Phone Number Redaction**
   - **Test Name**: `test_dotted_phone`
   - **Purpose**: To verify that phone numbers using dots as separators (e.g., "123.456.7890") are correctly redacted.
   - **Expected Output**: The phone number is replaced by redaction characters, and the count is updated.

4. **Plain Phone Number Redaction**
   - **Test Name**: `test_plain_phone`
   - **Purpose**: To verify that plain phone numbers without any separators (e.g., "1234567890") are correctly redacted.
   - **Expected Output**: The phone number is replaced by redaction characters, and the count is updated.

5. **Invalid Phone Number Preservation**
   - **Test Name**: `test_invalid_phone`
   - **Purpose**: To ensure that invalid phone numbers (e.g., "12345") are not mistakenly redacted.
   - **Expected Output**: The text remains unchanged, and the redaction count is zero.

- **`test_concepts.py`**:

The `test_concepts.py` file uses the `unittest` framework to verify the correctness of the `redact_concepts` function. Below is a summary of the main test cases included:

1. **Exact Concept Match Redaction**
   - **Test Name**: `test_exact_concept_match`
   - **Purpose**: To verify that sentences containing the exact concept (e.g., "conference") are correctly redacted.
   - **Expected Output**: The entire sentence containing the concept is replaced by the redaction character (`█`), and the count of redactions is correctly updated.

2. **No Concept Match**
   - **Test Name**: `test_no_concept_match`
   - **Purpose**: To ensure that sentences without the specified concept or its synonyms are not mistakenly redacted.
   - **Expected Output**: The text remains unchanged, and the redaction count is zero.

3. **Concept Synonym Redaction**
   - **Test Name**: `test_house_concept_redaction`
   - **Purpose**: To verify that sentences containing a concept (e.g., "house") or its synonyms (e.g., "mansion") are correctly redacted.
   - **Expected Output**: All sentences containing the concept or its synonyms are replaced by redaction characters, and the count is updated accordingly.


### Directory Structure
```
cis6930fa24-project1/
├── COLLABORATORS
├── LICENSE
├── README.md
├── Pipfile
├── docs/
├── redactor.py
├── setup.cfg
├── setup.py
└── tests/
    ├── test_names.py
    ├── test_dates.py
    ├── test_phones.py
    ├── test_address.py
    └── test_concepts.py
```

### Collaborators:
1. **StackOverflow**
   - https://stackoverflow.com/questions/11456670/regular-expression-for-address-field-validation
     - Helped in understanding and building regex patterns for address field validation.

2. **StackOverflow**
   - https://stackoverflow.com/questions/62824749/cosine-similarity-with-synonyms
     - Assisted in implementing cosine similarity for identifying synonyms in the redaction process.
3. **StackOverflow**
   - https://stackoverflow.com/questions/31199905/regex-for-extracting-meta-data
     - Provided insights for regex used to extract and redact metadata fields.

These resources were used as a guide to help develop some of the core functionalities in the project.



# Bugs and Assumptions

## Bugs

1. **Inconsistent Redaction for Synonyms**
   - The current implementation of concept redaction using cosine similarity may inconsistently redact sentences depending on the context. Synonyms that are not well-represented in the training data for the sentence transformer might not be identified correctly, leading to potential misses in redaction.

2. **Regex Overlapping Issues**
   - In some cases, overlapping patterns may lead to incorrect redaction when multiple regular expressions apply to a single segment of the text. This may result in partial redactions or unexpected text outputs.

3. **Performance Limitations with Large Files**
   - The redaction process, particularly for large text files, may suffer from performance issues due to repeated regex matching and NLP processing. This can result in slow processing times.

4. **NER False Positives**
   - The spaCy Named Entity Recognition (NER) model can produce false positives when identifying names, dates, or other entities, leading to unintended redactions of words that are not sensitive information.

5. **Formatting Issues Post-Redaction**
   - Redacting text with multiline strings sometimes results in formatting issues, such as excessive newline characters or unintended indentation changes, which could affect the readability of the redacted output.

## Assumptions

1. **Case Insensitivity**
   - All regex patterns are assumed to be case-insensitive to ensure consistent redaction across different text formats, regardless of capitalization.

2. **Common Folder Names**
   - In metadata fields, folder names like "Inbox," "Sent Items," and "Trash" are assumed to be non-sensitive and are not redacted, based on the assumption that these are generic terms.

3. **Durations Are Not Sensitive**
   - Durations (e.g., "3 weeks," "5 months") are assumed to be non-sensitive and are therefore not redacted during the date redaction process.

4. **Concept Matching Based on Similarity Threshold**
   - A similarity threshold of 0.6 is assumed to be sufficient for identifying related terms for concept redaction. This value was chosen to balance precision and recall, but it may not cover all possible variations of a concept.

5. **No Redaction of Short Words**
   - Words with fewer than three characters are assumed not to be sensitive and are therefore excluded from redaction. This helps to reduce the risk of over-redaction and preserves common short words.

6. **File Format Assumption**
   - The input files are assumed to be plain text files encoded in UTF-8. Files in other formats or encodings might not be processed correctly without additional handling.

7. **Metadata Redaction Scope**
   - Only specific metadata fields (e.g., "X-From," "X-To," "X-Origin") are targeted for redaction. Any additional metadata fields that are not explicitly defined may not be redacted.





### Submission
The project repository is hosted privately on GitHub and collaborators have been added as required. The submission follows all guidelines, including version tagging for grading (`v1.0`, `v2.0`, etc.).

### License
This project is licensed under the MIT License.





 




















