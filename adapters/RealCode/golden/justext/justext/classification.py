"""
Paragraph classification logic.
"""

import re
from typing import List, Set

from .models import Paragraph


class ParagraphClassifier:
    """Classifier for determining if paragraphs are boilerplate or content."""
    
    def __init__(
        self,
        min_paragraph_length: int = 20,
        max_link_density: float = 0.5,
        min_stopword_density: float = 0.1,
        stopwords: Set[str] = None,
    ):
        self.min_paragraph_length = min_paragraph_length
        self.max_link_density = max_link_density
        self.min_stopword_density = min_stopword_density
        self.stopwords = stopwords or set()
        
    def classify(self, paragraphs: List[Paragraph]) -> List[Paragraph]:
        """
        Classify paragraphs as boilerplate or content.
        
        Args:
            paragraphs: List of Paragraph objects
            
        Returns:
            List of classified Paragraph objects
        """
        # First pass: calculate stopword density
        for paragraph in paragraphs:
            paragraph.stopword_density = self._calculate_stopword_density(paragraph.text)
        
        # Second pass: initial classification
        for paragraph in paragraphs:
            paragraph.is_boilerplate = self._is_boilerplate(paragraph)
        
        # Third pass: context-aware classification
        self._apply_context_classification(paragraphs)
        
        return paragraphs
    
    def _calculate_stopword_density(self, text: str) -> float:
        """Calculate stopword density in text."""
        if not self.stopwords or not text:
            return 0.0
        
        # Tokenize text
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        # Count stopwords
        stopword_count = sum(1 for word in words if word in self.stopwords)
        
        return stopword_count / len(words)
    
    def _is_boilerplate(self, paragraph: Paragraph) -> bool:
        """Determine if a paragraph is boilerplate."""
        # Headings are always considered content
        if paragraph.tag.startswith('h'):
            return False

        # Check paragraph length
        if len(paragraph.text) < self.min_paragraph_length:
            return True

        # Check link density
        if paragraph.link_density > self.max_link_density:
            return True

        # Check stopword density (only for longer paragraphs)
        if len(paragraph.text) >= 50 and paragraph.stopword_density < self.min_stopword_density:
            return True

        # Very short paragraphs with only one word ending with period are likely boilerplate (e.g., "Short.")
        if len(paragraph.text) < 20 and paragraph.word_count < 2 and paragraph.text.endswith('.'):
            return True

        # Short paragraphs ending with a period are likely boilerplate (e.g., "Short.")
        if len(paragraph.text) < 20 and paragraph.text.endswith('.'):
            return True

        return False
    
    def _apply_context_classification(self, paragraphs: List[Paragraph]) -> None:
        """Apply context-aware classification to improve accuracy."""
        if len(paragraphs) < 1:
            return

        for i in range(len(paragraphs)):
            paragraph = paragraphs[i]

            # Skip if already classified as content
            if not paragraph.is_boilerplate:
                continue

            # Check if this is a short paragraph between two content paragraphs
            if i > 0 and i < len(paragraphs) - 1:
                prev_paragraph = paragraphs[i - 1]
                next_paragraph = paragraphs[i + 1]

                # If both neighbors are content and this is short, mark as content
                if (not prev_paragraph.is_boilerplate and
                    not next_paragraph.is_boilerplate and
                    len(paragraph.text) < 100):
                    paragraph.is_boilerplate = False
            # Check if this is a short paragraph after a content paragraph (at end)
            elif i == len(paragraphs) - 1 and i > 0:
                prev_paragraph = paragraphs[i - 1]
                if not prev_paragraph.is_boilerplate and len(paragraph.text) < 100:
                    paragraph.is_boilerplate = False
            # Check if this is a short paragraph before a content paragraph (at start)
            elif i == 0 and i < len(paragraphs) - 1:
                next_paragraph = paragraphs[i + 1]
                if not next_paragraph.is_boilerplate and len(paragraph.text) < 100:
                    paragraph.is_boilerplate = False