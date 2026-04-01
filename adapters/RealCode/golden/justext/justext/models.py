"""
Data models for jusText library.
"""

from dataclasses import dataclass


@dataclass
class Paragraph:
    """Represents a paragraph extracted from HTML."""
    text: str
    is_boilerplate: bool = False
    word_count: int = 0
    link_density: float = 0.0
    stopword_density: float = 0.0
    tag: str = ""
    
    def __str__(self) -> str:
        return self.text


class JustextError(Exception):
    """Base exception for jusText library."""
    pass