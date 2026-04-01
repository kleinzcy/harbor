"""
jusText - Web Content Extraction Library

A Python library that accurately extracts main body content from multilingual
web pages by efficiently parsing HTML, using heuristic content recognition,
and leveraging extensive stopword lists to automatically filter out boilerplate
content like navigation, ads, headers, and footers.
"""

from .models import Paragraph, JustextError
from .core import (
    extract_text,
    get_available_languages,
    load_stoplist,
    DEFAULT_PARAMS,
)

__version__ = "1.0.0"
__all__ = [
    "extract_text",
    "Paragraph",
    "JustextError",
    "get_available_languages",
    "load_stoplist",
    "DEFAULT_PARAMS",
]