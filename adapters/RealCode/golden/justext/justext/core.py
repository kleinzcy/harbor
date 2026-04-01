"""
Core functionality for jusText library.
"""

from typing import List, Optional, Union

from .models import Paragraph
from .html_parser import HTMLParser
from .classification import ParagraphClassifier
from .stopwords import StopwordsManager
from .encoding import EncodingDetector


DEFAULT_PARAMS = {
    "min_paragraph_length": 0,
    "max_link_density": 0.5,
    "min_stopword_density": 0.1,
    "language": "english",
    "encoding": None,
    "remove_scripts": True,
    "remove_styles": True,
    "remove_comments": True,
}


def extract_text(
    html: Union[str, bytes],
    language: str = "english",
    encoding: Optional[str] = None,
    min_paragraph_length: int = 0,
    max_link_density: float = 0.5,
    min_stopword_density: float = 0.1,
    remove_scripts: bool = True,
    remove_styles: bool = True,
    remove_comments: bool = True,
) -> List[Paragraph]:
    """
    Extract text paragraphs from HTML content.
    
    Args:
        html: HTML content as string or bytes
        language: Language for stopword analysis
        encoding: Character encoding (auto-detected if None)
        min_paragraph_length: Minimum paragraph length in characters
        max_link_density: Maximum link density for content paragraphs
        min_stopword_density: Minimum stopword density for content paragraphs
        remove_scripts: Whether to remove script tags
        remove_styles: Whether to remove style tags
        remove_comments: Whether to remove HTML comments
        
    Returns:
        List of Paragraph objects
    """
    # Detect encoding if needed
    if isinstance(html, bytes) and encoding is None:
        encoding = EncodingDetector.detect(html)
    
    # Parse HTML
    parser = HTMLParser(
        remove_scripts=remove_scripts,
        remove_styles=remove_styles,
        remove_comments=remove_comments,
    )
    paragraphs = parser.parse(html, encoding)
    
    # Load stopwords
    stopwords_manager = StopwordsManager()
    stopwords = stopwords_manager.get_stopwords(language)
    
    # Classify paragraphs
    classifier = ParagraphClassifier(
        min_paragraph_length=min_paragraph_length,
        max_link_density=max_link_density,
        min_stopword_density=min_stopword_density,
        stopwords=stopwords,
    )
    
    classified_paragraphs = classifier.classify(paragraphs)
    
    return classified_paragraphs


def get_available_languages() -> List[str]:
    """Get list of available languages for stopword lists."""
    manager = StopwordsManager()
    return manager.get_available_languages()


def load_stoplist(language: str) -> List[str]:
    """Load stopword list for a specific language."""
    manager = StopwordsManager()
    return manager.get_stopword_list(language)