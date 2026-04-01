"""
Utility functions for jusText library.
"""

import re
from typing import List
from bs4 import Tag


class LinkDensityCalculator:
    """Calculate link density for HTML elements."""
    
    @staticmethod
    def calculate(element: Tag) -> float:
        """
        Calculate link density for an HTML element.
        
        Args:
            element: BeautifulSoup Tag object
            
        Returns:
            Link density ratio (0.0 to 1.0)
        """
        total_text = element.get_text(strip=True)
        if not total_text:
            return 0.0
        
        link_text_length = LinkDensityCalculator._get_link_text_length(element)
        
        return link_text_length / len(total_text)
    
    @staticmethod
    def _get_link_text_length(element: Tag) -> int:
        """Get total length of text inside link tags."""
        link_text_length = 0
        links = element.find_all('a')
        
        for link in links:
            link_text = link.get_text(strip=True)
            link_text_length += len(link_text)
        
        return link_text_length


class TextCleaner:
    """Clean and normalize text."""
    
    @staticmethod
    def clean(text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Input text
            
        Returns:
            Word count
        """
        words = re.findall(r'\b\w+\b', text)
        return len(words)


class HTMLPreprocessor:
    """Preprocess HTML before parsing."""
    
    @staticmethod
    def remove_non_content(html: str) -> str:
        """
        Remove non-content elements from HTML.
        
        Args:
            html: HTML string
            
        Returns:
            Cleaned HTML
        """
        # Remove script tags
        html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags
        html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Remove head section
        html = re.sub(r'<head\b[^>]*>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        return html