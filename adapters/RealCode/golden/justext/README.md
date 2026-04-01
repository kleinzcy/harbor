# jusText - Web Content Extraction Library

jusText is a Python library that accurately extracts main body content from multilingual web pages by efficiently parsing HTML, using heuristic content recognition, and leveraging extensive stopword lists to automatically filter out boilerplate content like navigation, ads, headers, and footers.

## Features

- **Basic Text Extraction**: Extract clean text paragraphs from HTML documents
- **Boilerplate Detection**: Automatically identify and filter boilerplate content
- **Encoding Handling**: Automatic encoding detection and proper decoding
- **Multi-language Support**: Stoplist support for 80+ languages
- **HTML Preprocessing**: Automatic removal of script, style, and comment tags
- **Context-Based Classification**: Smart classification considering neighboring paragraphs
- **Link Density Calculation**: Accurate link density metrics for boilerplate detection

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start

### Basic Usage

```python
from justext import extract_text

html = """
<html>
<body>
    <h1>Article Title</h1>
    <p>This is the main content of the article.</p>
    <nav><a href="#">Home</a><a href="#">About</a></nav>
    <p>Another paragraph with useful information.</p>
</body>
</html>
"""

paragraphs = extract_text(html)

for paragraph in paragraphs:
    if not paragraph.is_boilerplate:
        print(paragraph.text)
```

### Command Line Interface

```bash
# Extract text from HTML file
cat input.html | python extract_text.py

# Use specific language
cat input.html | python extract_text.py --language german

# Adjust extraction parameters
cat input.html | python extract_text.py --min-length 30 --max-link-density 0.4
```

## API Reference

### `extract_text()`

```python
extract_text(
    html: Union[str, bytes],
    language: str = "english",
    encoding: Optional[str] = None,
    min_paragraph_length: int = 20,
    max_link_density: float = 0.5,
    min_stopword_density: float = 0.1,
    remove_scripts: bool = True,
    remove_styles: bool = True,
    remove_comments: bool = True,
) -> List[Paragraph]
```

Extract text paragraphs from HTML content.

**Parameters:**
- `html`: HTML content as string or bytes
- `language`: Language for stopword analysis (default: "english")
- `encoding`: Character encoding (auto-detected if None)
- `min_paragraph_length`: Minimum paragraph length in characters (default: 20)
- `max_link_density`: Maximum link density for content paragraphs (default: 0.5)
- `min_stopword_density`: Minimum stopword density for content paragraphs (default: 0.1)
- `remove_scripts`: Whether to remove script tags (default: True)
- `remove_styles`: Whether to remove style tags (default: True)
- `remove_comments`: Whether to remove HTML comments (default: True)

**Returns:** List of `Paragraph` objects

### `Paragraph` Class

```python
@dataclass
class Paragraph:
    text: str                    # Text content
    is_boilerplate: bool = False # Whether paragraph is boilerplate
    word_count: int = 0          # Number of words
    link_density: float = 0.0    # Ratio of link text to total text
    stopword_density: float = 0.0 # Ratio of stopwords to total words
    tag: str = ""                # HTML tag the paragraph came from
```

### Utility Functions

```python
# Get available languages
from justext import get_available_languages
languages = get_available_languages()

# Load stopword list
from justext import load_stoplist
stopwords = load_stoplist("german")
```

## Language Support

jusText supports the following languages (with more being added):

- English
- German
- French
- Spanish
- Italian
- Portuguese
- Dutch
- Russian
- Chinese
- Japanese
- Korean
- Arabic

To see all available languages:

```bash
python extract_text.py --list-languages
```

## Testing

Run the full test suite:

```bash
cd tests
bash test.sh
```

Or run tests individually:

```bash
cd tests
python run_tests.py > stdout.txt
```

## How It Works

1. **HTML Parsing**: The library uses BeautifulSoup to parse HTML and extract text from block-level elements.
2. **Preprocessing**: Script, style, and comment tags are removed to focus on content.
3. **Paragraph Extraction**: Text is extracted from paragraphs, headings, and other content containers.
4. **Feature Calculation**: For each paragraph, features like link density and stopword density are calculated.
5. **Classification**: Paragraphs are classified as content or boilerplate based on heuristics.
6. **Context Analysis**: Short paragraphs between content paragraphs are preserved based on context.

## Configuration

You can customize the extraction behavior by adjusting these parameters:

- `min_paragraph_length`: Increase for stricter filtering, decrease for more inclusive extraction
- `max_link_density`: Decrease to filter out more navigation-heavy content
- `min_stopword_density`: Increase to require more common words in content paragraphs
- `language`: Set to match the language of your content for better stopword analysis

## Performance Considerations

- The library uses lxml as the HTML parser backend for better performance
- Stopwords are cached after first load for each language
- Encoding detection happens only when needed (for bytes input)
- Large HTML documents are processed efficiently with streaming where possible

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.