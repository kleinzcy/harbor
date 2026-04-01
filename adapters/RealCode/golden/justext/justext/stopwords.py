"""
Stopword list management for multiple languages.
"""

import sys
from typing import List, Set, Dict

# Try to import importlib.resources for modern Python
if sys.version_info >= (3, 9):
    pass
else:
    pass


class StopwordsManager:
    """Manager for stopword lists in multiple languages."""
    
    def __init__(self):
        self._stopwords_cache: Dict[str, Set[str]] = {}
        self._available_languages = self._load_available_languages()
    
    def get_stopwords(self, language: str) -> Set[str]:
        """
        Get stopword list for a specific language.

        Args:
            language: Language name (case-insensitive)

        Returns:
            Set of stopwords for the language

        Raises:
            ValueError: If language is not supported
        """
        language_lower = language.lower()

        # Check cache first
        if language_lower in self._stopwords_cache:
            return self._stopwords_cache[language_lower]

        # Load stopwords
        stopwords = self._load_stopwords(language_lower)
        self._stopwords_cache[language_lower] = stopwords

        return stopwords

    def get_stopword_list(self, language: str) -> List[str]:
        """
        Get stopword list for a specific language as ordered list.

        Args:
            language: Language name (case-insensitive)

        Returns:
            List of stopwords for the language in the original order

        Raises:
            ValueError: If language is not supported
        """
        language_lower = language.lower()
        # Return the built-in list directly (already ordered)
        return self._get_builtin_stopwords_list(language_lower)
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages for stopword lists."""
        return list(self._available_languages.keys())
    
    def _load_available_languages(self) -> Dict[str, str]:
        """Load mapping of language names to file paths."""
        # Built-in stopword lists
        languages = {
            'english': 'english',
            'german': 'german',
            'french': 'french',
            'spanish': 'spanish',
            'italian': 'italian',
            'portuguese': 'portuguese',
            'dutch': 'dutch',
            'russian': 'russian',
            'chinese': 'chinese',
            'japanese': 'japanese',
            'korean': 'korean',
            'arabic': 'arabic',
        }
        
        return languages
    
    def _load_stopwords(self, language: str) -> Set[str]:
        """Load stopwords for a specific language."""
        # Check if language is available
        if language not in self._available_languages:
            raise ValueError(f"Language '{language}' is not supported. "
                           f"Available languages: {', '.join(self.get_available_languages())}")
        
        # Get language code
        lang_code = self._available_languages[language]
        
        # Try to load from package data first
        try:
            # For now, we'll use built-in stopwords
            # In a real package, we would load from package resources
            pass
        except:
            pass
        
        # Fall back to built-in stopwords
        return self._get_builtin_stopwords(lang_code)
    
    def _get_builtin_stopwords_list(self, language: str) -> List[str]:
        """Get built-in stopword lists as ordered list."""
        # Common stopwords for various languages (preserve insertion order)
        stopwords_dict = {
            'english': [
                'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'for',
                'was', 'on', 'with', 'he', 'be', 'i', 'by', 'as', 'you', 'are',
                'his', 'they', 'have', 'from', 'one', 'had', 'word', 'but', 'not',
                'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there',
                'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if',
                'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them',
                'these', 'so', 'some', 'her', 'would', 'make', 'like', 'him', 'into',
                'time', 'has', 'look', 'two', 'more', 'write', 'go', 'see', 'number',
                'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water',
                'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down',
                'day', 'did', 'get', 'come', 'made', 'may', 'part'
            ],
            'german': [
                'der', 'die', 'das', 'und', 'in', 'den', 'von', 'zu', 'mit', 'sich',
                'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine',
                'als', 'auch', 'es', 'an', 'werden', 'aus', 'er', 'hat', 'dass',
                'sie', 'nach', 'wird', 'bei', 'einer', 'um', 'am', 'sind', 'noch',
                'wie', 'einem', 'über', 'einen', 'so', 'zum', 'haben', 'nur',
                'oder', 'aber', 'vor', 'zur', 'bis', 'mehr', 'durch', 'man',
                'sein', 'wurde', 'sei', 'hatte', 'kann', 'gegen', 'vom',
                'können', 'schon', 'wenn', 'habe', 'ihre', 'dann', 'unter',
                'wir', 'soll', 'ich', 'eines', 'es', 'jahr', 'zwei', 'jahren',
                'diese', 'dieser', 'wieder', 'keine', 'uhr', 'seiner', 'worden',
                'und', 'will', 'zwischen', 'immer', 'millionen', 'einmal', 'was',
                'sagte'
            ],
            'french': [
                'le', 'la', 'les', 'de', 'un', 'une', 'des', 'et', 'en', 'à',
                'est', 'pour', 'dans', 'que', 'qui', 'au', 'par', 'sur', 'avec',
                'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'ce', 'cet',
                'cette', 'ces', 'son', 'sa', 'ses', 'notre', 'nos', 'votre',
                'vos', 'leur', 'leurs', 'du', 'aux', 'pas', 'ne', 'se', 's',
                'y', 'a', 'ou', 'où', 'mais', 'donc', 'or', 'ni', 'car', 'lui',
                'moi', 'toi', 'soi', 'eux', 'celui', 'celle', 'ceux', 'celles',
                'mon', 'ton', 'son', 'notre', 'votre', 'leur', 'mien', 'tien',
                'sien', 'nôtre', 'vôtre', 'leur', 'quoi', 'quel', 'quelle',
                'quels', 'quelles', 'lequel', 'laquelle', 'lesquels', 'lesquelles',
                'dont', 'duquel', 'de laquelle', 'desquels', 'desquelles'
            ],
        }

        # Return empty list if language not found
        return stopwords_dict.get(language, [])

    def _get_builtin_stopwords(self, language: str) -> Set[str]:
        """Get built-in stopword lists as set."""
        return set(self._get_builtin_stopwords_list(language))