# jusText - Web Content Extraction Library

## Project Goal

Build a Python library that accurately extracts main body content from multilingual web pages by efficiently parsing HTML, using heuristic content recognition, and leveraging extensive stopword lists to automatically filter out boilerplate content like navigation, ads, headers, and footers. The library allows developers to extract clean, relevant text from web pages without dealing with the complexities of HTML parsing, encoding detection, and noise filtering.

---

## Background & Problem

Without this library/tool, developers are forced to manually parse HTML documents, write custom regex patterns, or use complex XPath/CSS selectors to extract content. This leads to brittle code that breaks with different website layouts, requires constant maintenance, and fails to handle multilingual content effectively. Developers must also manually handle encoding detection, remove script/style tags, and implement boilerplate detection algorithms from scratch.

With this library/tool, developers can simply pass HTML content and receive clean, extracted text with automatic boilerplate filtering. The library handles encoding detection, multilingual stopword analysis, and intelligent content classification, providing a streamlined experience for web content extraction across diverse websites and languages.

---

## Core Features

### Feature 1: Basic Text Extraction

**As a developer**, I want to extract clean text paragraphs from HTML documents, so I can get structured content without HTML tags.

**Expected Behavior / Usage:**

The library should parse HTML input and return a list of Paragraph objects containing extracted text. Each paragraph should include the text content, word count, and basic metadata. The API should accept HTML as string or bytes and a stoplist for language-specific processing.

**Test Cases:** `tests/test_cases/feature1_basic_extraction.json`

```json
{
    "description": "Basic HTML text extraction with simple paragraphs",
    "cases": [
        {
            "input": "<p>Hello world</p>",
            "expected_output": "Hello world"
        },
        {
            "input": "<div><p>First paragraph</p><p>Second paragraph</p></div>",
            "expected_output": "First paragraph\nSecond paragraph"
        },
        {
            "input": "<h1>Title</h1><p>Content</p>",
            "expected_output": "Title\nContent"
        }
    ]
}
```

---

### Feature 2: Boilerplate Detection

**As a developer**, I want to automatically identify and filter boilerplate content, so I can focus on the main article text.

**Expected Behavior / Usage:**

The library should classify paragraphs as boilerplate or content based on heuristics like link density, text length, and stopword frequency. Paragraphs with high link density or very short text should be marked as boilerplate. The API should provide a boolean flag `is_boilerplate` on each Paragraph object.

**Test Cases:** `tests/test_cases/feature2_boilerplate_detection.json`

```json
{
    "description": "Detection of boilerplate content based on link density and text characteristics",
    "cases": [
        {
            "input": "<div><a href=\"#\">Link1</a><a href=\"#\">Link2</a><a href=\"#\">Link3</a>Short text</div>",
            "expected_output": ""
        },
        {
            "input": "<p>This is a long paragraph with many common words like the, and, is, which are typical stopwords in English. It contains useful information.</p>",
            "expected_output": "This is a long paragraph with many common words like the, and, is, which are typical stopwords in English. It contains useful information."
        },
        {
            "input": "<p>Short.</p>",
            "expected_output": ""
        }
    ]
}
```

---

### Feature 3: Encoding Handling

**As a developer**, I want automatic encoding detection and proper decoding, so I can process HTML from various sources without manual encoding specification.

**Expected Behavior / Usage:**

The library should automatically detect encoding from HTML meta tags or byte patterns, and properly decode the content. It should accept both string and bytes input, and provide optional parameters to override encoding or error handling.

**Test Cases:** `tests/test_cases/feature3_encoding_handling.json`

```json
{
    "description": "Automatic encoding detection and decoding for various HTML inputs",
    "cases": [
        {
            "input": "<p>Hello 世界</p>",
            "expected_output": "Hello 世界"
        },
        {
            "input": "<meta charset=\"utf-8\"><p>Test content</p>",
            "expected_output": "Test content"
        },
        {
            "input": "<meta charset=\"iso-8859-1\"><p>Test</p>",
            "expected_output": "Test"
        }
    ]
}
```

---

### Feature 4: Multi-language Support

**As a developer**, I want stoplist support for 80+ languages, so I can accurately process content in different languages.

**Expected Behavior / Usage:**

The library should provide stopword lists for multiple languages to improve boilerplate detection accuracy. It should include functions to get available languages, load specific stoplists, and handle case-insensitive language names. Unknown languages should raise appropriate errors.

**Test Cases:** `tests/test_cases/feature4_multilingual_support.json`

```json
{
    "description": "Support for multiple languages through stopword lists",
    "cases": [
        {
            "input": "English",
            "expected_output": "[\"the\", \"and\", \"is\", \"in\", \"to\", \"of\", \"a\", \"that\", \"it\", \"for\"]"
        },
        {
            "input": "German",
            "expected_output": "[\"der\", \"die\", \"das\", \"und\", \"in\", \"den\", \"von\", \"zu\", \"mit\", \"sich\"]"
        },
        {
            "input": "French",
            "expected_output": "[\"le\", \"la\", \"les\", \"de\", \"un\", \"une\", \"des\", \"et\", \"en\", \"à\"]"
        }
    ]
}
```

---

### Feature 5: HTML Preprocessing

**As a developer**, I want automatic removal of script, style, and comment tags, so I can work with clean HTML content.

**Expected Behavior / Usage:**

The library should preprocess HTML by removing non-content elements before extraction. This includes script tags, style tags, HTML comments, and head sections. The preprocessing should be transparent to the user but configurable if needed.

**Test Cases:** `tests/test_cases/feature5_html_preprocessing.json`

```json
{
    "description": "Removal of non-content HTML elements before text extraction",
    "cases": [
        {
            "input": "<body><script>alert('test')</script><p>Real content</p></body>",
            "expected_output": "Real content"
        },
        {
            "input": "<body><style>.class { color: red; }</style><p>Text</p></body>",
            "expected_output": "Text"
        },
        {
            "input": "<body><!-- Comment --><p>Content</p></body>",
            "expected_output": "Content"
        }
    ]
}
```

---

### Feature 6: Context-Based Classification

**As a developer**, I want smart classification that considers neighboring paragraphs, so short but relevant paragraphs aren't incorrectly filtered.

**Expected Behavior / Usage:**

The library should use contextual information to improve classification accuracy. Short paragraphs between long content paragraphs should be considered content, while isolated short paragraphs should be filtered. This requires analyzing paragraph relationships during classification.

**Test Cases:** `tests/test_cases/feature6_context_classification.json`

```json
{
    "description": "Context-aware paragraph classification considering neighboring content",
    "cases": [
        {
            "input": "<div><p>Long good paragraph with many words and sufficient length.</p><p>Short.</p><p>Another long good paragraph with adequate length.</p></div>",
            "expected_output": "Long good paragraph with many words and sufficient length.\nShort.\nAnother long good paragraph with adequate length."
        },
        {
            "input": "<div><nav><a>Link1</a><a>Link2</a></nav><p>Good content here</p><footer><a>Footer</a></footer></div>",
            "expected_output": "Good content here"
        }
    ]
}
```

---

### Feature 7: Link Density Calculation

**As a developer**, I want accurate link density metrics for boilerplate detection, so I can identify navigation-heavy content.

**Expected Behavior / Usage:**

The library should calculate link density (ratio of link text to total text) for each paragraph. High link density indicates navigation or advertisement content. The link density should be available as a property on Paragraph objects and used in classification decisions.

**Test Cases:** `tests/test_cases/feature7_link_density.json`

```json
{
    "description": "Calculation and use of link density for content classification",
    "cases": [
        {
            "input": "<p><a href=\"#\">Link1</a><a href=\"#\">Link2</a><a href=\"#\">Link3</a>text</p>",
            "expected_output": ""
        },
        {
            "input": "<p>This is a long paragraph with only one <a href=\"#\">link</a> and plenty of regular text.</p>",
            "expected_output": "This is a long paragraph with only one link and plenty of regular text."
        },
        {
            "input": "<p>Plain text without any links</p>",
            "expected_output": "Plain text without any links"
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_[name].json` should write its output to `tests/stdout/feature1_[name]@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.

3. **Core library implementation** including:
   - HTML parsing and preprocessing module
   - Paragraph extraction and classification logic
   - Stopword list management for multiple languages
   - Encoding detection and handling
   - Context-aware classification algorithms
   - Link density calculation utilities

4. **Documentation** covering:
   - API reference with usage examples
   - Installation and setup instructions
   - Configuration options for tuning extraction parameters
   - Language support documentation
   - Performance considerations and best practices