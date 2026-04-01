"""
Content matching module for source code search.
"""
import re
from dataclasses import dataclass
from typing import List, Iterator, Optional


@dataclass
class MatchResult:
    """Result of a content match in a single line."""
    matching_line: str
    matching_lineno: int
    matching_column_ranges: List[List[int]]  # list of [start, end)


class ContentMatcher:
    """
    Matches content against a pattern with various options.

    Supports regex, literal, case-insensitive, whole-word, inverted,
    smart-case, and max-match options.
    """

    def __init__(
        self,
        pattern: str,
        ignore_case: bool = False,
        smart_case: bool = False,
        whole_words: bool = False,
        literal_pattern: bool = False,
        invert_match: bool = False,
        max_match_count: Optional[int] = None,
    ):
        """
        Initialize ContentMatcher.

        Args:
            pattern: Search pattern
            ignore_case: Case-insensitive matching
            smart_case: Automatically determine case sensitivity based on pattern
            whole_words: Match whole words only
            literal_pattern: Treat pattern as literal string, not regex
            invert_match: Return non-matching lines
            max_match_count: Maximum number of matches to return per file
        """
        self.pattern = pattern
        self.ignore_case = ignore_case
        self.smart_case = smart_case
        self.whole_words = whole_words
        self.literal_pattern = literal_pattern
        self.invert_match = invert_match
        self.max_match_count = max_match_count

        # Determine actual case sensitivity
        if smart_case:
            # If pattern contains any uppercase letters, be case-sensitive
            self.case_sensitive = any(c.isupper() for c in pattern)
        else:
            self.case_sensitive = not ignore_case

        # Compile regex or prepare literal matcher
        if literal_pattern:
            self.regex = None
            self.literal_pattern = pattern
        else:
            regex_pattern = pattern
            if whole_words:
                # Add word boundaries - \b matches at word boundaries
                regex_pattern = r'\b' + regex_pattern + r'\b'

            flags = 0
            if not self.case_sensitive:
                flags |= re.IGNORECASE

            try:
                self.regex = re.compile(regex_pattern, flags)
            except re.error:
                # If regex compilation fails, treat as literal pattern
                self.regex = None
                self.literal_pattern = re.escape(pattern)

    def match_lines(self, content: str) -> Iterator[MatchResult]:
        """
        Match pattern against content line by line.

        Args:
            content: String content to search

        Yields:
            MatchResult for each matching line (or non-matching if invert_match)
        """
        lines = content.splitlines(keepends=False)
        match_count = 0

        for lineno, line in enumerate(lines, start=1):
            # Determine if this line matches
            matches = self._line_matches(line)
            column_ranges = self._get_column_ranges(line) if matches else []

            # Apply invert_match logic
            if self.invert_match:
                # Return lines that do NOT match
                if not matches:
                    yield MatchResult(
                        matching_line=line,
                        matching_lineno=lineno,
                        matching_column_ranges=[]
                    )
                    match_count += 1
            else:
                # Return lines that match
                if matches:
                    yield MatchResult(
                        matching_line=line,
                        matching_lineno=lineno,
                        matching_column_ranges=column_ranges
                    )
                    match_count += 1

            # Check max match count
            if self.max_match_count is not None and match_count >= self.max_match_count:
                break

    def _line_matches(self, line: str) -> bool:
        """Check if line matches the pattern."""
        if self.regex is not None:
            return bool(self.regex.search(line))
        else:
            # Literal pattern matching
            pattern = self.literal_pattern
            if not self.case_sensitive:
                line_lower = line.lower()
                pattern_lower = pattern.lower()
                return pattern_lower in line_lower
            else:
                return pattern in line

    def _get_column_ranges(self, line: str) -> List[List[int]]:
        """Get column ranges of all matches in line."""
        if self.regex is not None:
            # Find all non-overlapping matches
            ranges = []
            for match in self.regex.finditer(line):
                start = match.start()
                end = match.end()
                ranges.append([start, end])
            return ranges
        else:
            # Literal pattern matching - find all occurrences
            pattern = self.literal_pattern
            ranges = []
            start = 0
            if not self.case_sensitive:
                line_lower = line.lower()
                pattern_lower = pattern.lower()
                while True:
                    pos = line_lower.find(pattern_lower, start)
                    if pos == -1:
                        break
                    ranges.append([pos, pos + len(pattern)])
                    start = pos + 1
            else:
                while True:
                    pos = line.find(pattern, start)
                    if pos == -1:
                        break
                    ranges.append([pos, pos + len(pattern)])
                    start = pos + 1
            return ranges


def matcher(
    pattern: str,
    ignore_case: bool = False,
    smart_case: bool = False,
    whole_words: bool = False,
    literal_pattern: bool = False,
    invert_match: bool = False,
    max_match_count: Optional[int] = None,
    content: str = "",
) -> List[MatchResult]:
    """
    Convenience function to match content and return list of MatchResults.

    This is the interface expected by the test runner.
    """
    matcher = ContentMatcher(
        pattern=pattern,
        ignore_case=ignore_case,
        smart_case=smart_case,
        whole_words=whole_words,
        literal_pattern=literal_pattern,
        invert_match=invert_match,
        max_match_count=max_match_count,
    )
    return list(matcher.match_lines(content))


if __name__ == '__main__':
    # Simple test
    results = matcher(
        pattern="def ",
        ignore_case=False,
        max_match_count=2,
        content="def foo():\n  print('def')\ndef bar():\n  pass"
    )
    for r in results:
        print(r)