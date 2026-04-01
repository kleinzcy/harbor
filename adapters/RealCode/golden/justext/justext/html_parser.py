"""
HTML parsing and preprocessing module.
"""

from typing import List, Union, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
from bs4.element import Comment

from .models import Paragraph


class HTMLParser:
    """HTML parser for extracting text paragraphs."""
    
    def __init__(
        self,
        remove_scripts: bool = True,
        remove_styles: bool = True,
        remove_comments: bool = True,
    ):
        self.remove_scripts = remove_scripts
        self.remove_styles = remove_styles
        self.remove_comments = remove_comments
        
    def parse(self, html: Union[str, bytes], encoding: Optional[str] = None) -> List[Paragraph]:
        """
        Parse HTML and extract paragraphs.
        
        Args:
            html: HTML content as string or bytes
            encoding: Character encoding (for bytes input)
            
        Returns:
            List of Paragraph objects
        """
        # Convert bytes to string if needed
        if isinstance(html, bytes):
            if encoding:
                html_str = html.decode(encoding, errors='replace')
            else:
                html_str = html.decode('utf-8', errors='replace')
        else:
            html_str = html
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_str, 'lxml')
        
        # Remove non-content elements
        self._remove_non_content(soup)
        
        # Extract paragraphs
        paragraphs = self._extract_paragraphs(soup)
        
        return paragraphs
    
    def _remove_non_content(self, soup: BeautifulSoup) -> None:
        """Remove script, style, and comment tags from HTML."""
        if self.remove_scripts:
            for script in soup.find_all('script'):
                script.decompose()
        
        if self.remove_styles:
            for style in soup.find_all('style'):
                style.decompose()
        
        if self.remove_comments:
            for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
                comment.extract()
        
        # Also remove head section
        head = soup.find('head')
        if head:
            head.decompose()
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[Paragraph]:
        """Extract text paragraphs from HTML."""
        paragraphs = []
        
        # First, extract all heading elements (h1-h6)
        heading_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for element in heading_elements:
            text = self._get_element_text(element)
            if text:
                link_text_length = self._get_link_text_length(element)
                total_text_length = len(text)
                link_density = link_text_length / total_text_length if total_text_length > 0 else 0.0
                
                paragraph = Paragraph(
                    text=text.strip(),
                    tag=element.name,
                    link_density=link_density,
                    word_count=len(text.split()),
                )
                paragraphs.append(paragraph)
        
        # Then extract all paragraph elements
        p_elements = soup.find_all('p')
        for element in p_elements:
            text = self._get_element_text(element)
            if text:
                link_text_length = self._get_link_text_length(element)
                total_text_length = len(text)
                link_density = link_text_length / total_text_length if total_text_length > 0 else 0.0
                
                paragraph = Paragraph(
                    text=text.strip(),
                    tag=element.name,
                    link_density=link_density,
                    word_count=len(text.split()),
                )
                paragraphs.append(paragraph)
        
        # If we found headings or paragraphs, don't extract from parent divs
        if paragraphs:
            return paragraphs
        
        # Otherwise, extract from headings and other block elements
        other_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'div'])
        for element in other_elements:
            # Skip if this element contains any paragraph we already extracted
            if element.find('p'):
                continue
                
            text = self._get_element_text(element)
            if text:
                link_text_length = self._get_link_text_length(element)
                total_text_length = len(text)
                link_density = link_text_length / total_text_length if total_text_length > 0 else 0.0
                
                paragraph = Paragraph(
                    text=text.strip(),
                    tag=element.name,
                    link_density=link_density,
                    word_count=len(text.split()),
                )
                paragraphs.append(paragraph)
        
        return paragraphs
        
        # If no block elements found, extract text from body
        if not paragraphs and soup.body:
            text = soup.body.get_text(separator=' ', strip=True)
            if text:
                link_text_length = self._get_link_text_length(soup.body)
                total_text_length = len(text)
                link_density = link_text_length / total_text_length if total_text_length > 0 else 0.0
                
                paragraph = Paragraph(
                    text=text,
                    tag='body',
                    link_density=link_density,
                    word_count=len(text.split()),
                )
                paragraphs.append(paragraph)
        
        return paragraphs
    
    def _get_element_text(self, element: Tag) -> str:
        """Get text content from an HTML element."""
        # Get text with proper spacing
        texts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    texts.append(text)
            elif child.name in ['br', 'hr']:
                texts.append('\n')
            elif child.name not in ['script', 'style']:
                child_text = self._get_element_text(child)
                if child_text:
                    texts.append(child_text)
        
        # Join with space, but preserve paragraph separation
        return ' '.join(texts)
    
    def _get_link_text_length(self, element: Tag) -> int:
        """Get total length of text inside link tags."""
        link_text_length = 0
        links = element.find_all('a')
        
        for link in links:
            link_text = link.get_text(strip=True)
            link_text_length += len(link_text)
        
        return link_text_length