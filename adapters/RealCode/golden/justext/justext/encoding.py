"""
Encoding detection and handling module.
"""

import re
import chardet
from typing import Optional


class EncodingDetector:
    """Detect and handle character encoding for HTML content."""
    
    @staticmethod
    def detect(html_bytes: bytes) -> str:
        """
        Detect character encoding from HTML bytes.
        
        Args:
            html_bytes: HTML content as bytes
            
        Returns:
            Detected encoding as string
        """
        # First, try to detect encoding from HTML meta tags
        encoding = EncodingDetector._detect_from_meta(html_bytes)
        if encoding:
            return encoding
        
        # Fall back to chardet
        result = chardet.detect(html_bytes)
        return result.get('encoding', 'utf-8')
    
    @staticmethod
    def _detect_from_meta(html_bytes: bytes) -> Optional[str]:
        """
        Detect encoding from HTML meta tags.
        
        Args:
            html_bytes: HTML content as bytes
            
        Returns:
            Encoding string or None if not found
        """
        # Decode a small portion for pattern matching
        try:
            sample = html_bytes[:5000].decode('ascii', errors='ignore')
        except:
            return None
        
        # Look for charset in meta tags
        charset_patterns = [
            r'<meta\s+charset=["\']?([^"\'>\s]+)["\']?',
            r'<meta\s+[^>]*content=["\'][^"\']*charset=([^"\'>\s]+)',
            r'<meta\s+http-equiv=["\']?Content-Type["\']?\s+content=["\'][^"\']*charset=([^"\'>\s]+)',
        ]
        
        for pattern in charset_patterns:
            match = re.search(pattern, sample, re.IGNORECASE)
            if match:
                encoding = match.group(1).lower()
                # Normalize common encoding names
                encoding = EncodingDetector._normalize_encoding(encoding)
                return encoding
        
        return None
    
    @staticmethod
    def _normalize_encoding(encoding: str) -> str:
        """Normalize encoding name to standard form."""
        encoding = encoding.lower()
        
        # Common aliases
        encoding_map = {
            'utf8': 'utf-8',
            'utf-8': 'utf-8',
            'iso-8859-1': 'iso-8859-1',
            'iso8859-1': 'iso-8859-1',
            'latin-1': 'iso-8859-1',
            'latin1': 'iso-8859-1',
            'windows-1252': 'windows-1252',
            'cp1252': 'windows-1252',
            'gb2312': 'gb2312',
            'gbk': 'gbk',
            'big5': 'big5',
            'shift_jis': 'shift_jis',
            'euc-jp': 'euc-jp',
        }
        
        return encoding_map.get(encoding, encoding)
    
    @staticmethod
    def decode(html_bytes: bytes, encoding: Optional[str] = None) -> str:
        """
        Decode HTML bytes to string.
        
        Args:
            html_bytes: HTML content as bytes
            encoding: Character encoding (auto-detected if None)
            
        Returns:
            Decoded HTML string
        """
        if encoding is None:
            encoding = EncodingDetector.detect(html_bytes)
        
        try:
            return html_bytes.decode(encoding, errors='replace')
        except (LookupError, UnicodeDecodeError):
            # Fall back to UTF-8 with error replacement
            return html_bytes.decode('utf-8', errors='replace')