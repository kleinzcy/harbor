# -*- coding: utf-8 -*-
"""Error handling for Pylama."""

import re
from typing import Dict, List, Set, Tuple, Optional, Any

# Pattern to extract error number from text
PATTERN_NUMBER = re.compile(r"^\s*([A-Z]\d+)\s*", re.I)

# Mapping of duplicate error codes between linters
DUPLICATES: Dict[Tuple[str, str], Set[Tuple[str, str]]] = {
    # multiple statements on one line
    ("pycodestyle", "E701"): {("pylint", "C0321")},
    # unused variable
    ("pylint", "W0612"): {("pyflakes", "W0612")},
    # undefined variable
    ("pylint", "E0602"): {("pyflakes", "E0602")},
    # unused import
    ("pylint", "W0611"): {("pyflakes", "W0611")},
    # whitespace before ')'
    ("pylint", "C0326"): {("pycodestyle", "E202")},
    # whitespace before '('
    ("pylint", "C0326"): {("pycodestyle", "E211")},
    # multiple spaces after operator
    ("pylint", "C0326"): {("pycodestyle", "E222")},
    # missing whitespace around operator
    ("pylint", "C0326"): {("pycodestyle", "E225")},
    # unexpected spaces
    ("pylint", "C0326"): {("pycodestyle", "E251")},
    # long lines
    ("pylint", "C0301"): {("pycodestyle", "E501")},
    # statement ends with a semicolon
    ("pylint", "W0301"): {("pycodestyle", "E703")},
    # multiple statements on one line
    ("pylint", "C0321"): {("pycodestyle", "E702")},
    # bad indentation
    ("pylint", "W0311"): {("pycodestyle", "E111")},
    # wildcard import
    ("pylint", "W00401"): {("pyflakes", "W0401")},
    # module docstring
    ("pydocstyle", "D100"): {("pylint", "C0111")},
}


class Error:
    """Represents a code checking error."""

    __slots__ = ("filename", "lnum", "col", "number", "text", "type", "source")

    def __init__(
        self,
        filename: str = "",
        lnum: int = 1,
        col: int = 0,
        text: str = "",
        number: str = "",
        type: str = "E",  # E for error, W for warning, etc.
        source: str = "",
    ):
        """Initialize an error.

        :param filename: File name
        :param lnum: Line number
        :param col: Column number
        :param text: Error message
        :param number: Error code (e.g., "E225")
        :param type: Error type (E, W, C, R, F, etc.)
        :param source: Error source (e.g., "pycodestyle", "pylint")
        """
        self.filename = filename
        self.lnum = lnum
        self.col = col
        self.text = text
        self.number = number
        self.type = type
        self.source = source

        # Extract number from text if not provided
        if not self.number and self.text:
            match = PATTERN_NUMBER.search(self.text)
            if match:
                self.number = match.group(1)

    def __str__(self) -> str:
        """Return formatted error information."""
        if self.col:
            return (
                f"{self.filename}:{self.lnum}:{self.col}: "
                f"{self.type}{self.number} {self.text} ({self.source})"
            )
        return (
            f"{self.filename}:{self.lnum}: "
            f"{self.type}{self.number} {self.text} ({self.source})"
        )

    def __repr__(self) -> str:
        """Return representation of the error."""
        return (
            f"Error(filename={self.filename!r}, lnum={self.lnum}, "
            f"col={self.col}, text={self.text!r}, number={self.number!r}, "
            f"type={self.type!r}, source={self.source!r})"
        )

    def __eq__(self, other: Any) -> bool:
        """Compare whether two errors are the same."""
        if not isinstance(other, Error):
            return False
        return (
            self.filename == other.filename
            and self.lnum == other.lnum
            and self.col == other.col
            and self.number == other.number
            and self.text == other.text
            and self.type == other.type
            and self.source == other.source
        )

    def __hash__(self) -> int:
        """Return hash for the error."""
        return hash(
            (
                self.filename,
                self.lnum,
                self.col,
                self.number,
                self.text,
                self.type,
                self.source,
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "filename": self.filename,
            "lnum": self.lnum,
            "col": self.col,
            "text": self.text,
            "number": self.number,
            "type": self.type,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Error":
        """Create error from dictionary."""
        return cls(**data)


def remove_duplicates(errors: List[Error]) -> List[Error]:
    """Remove duplicate items from the error list.

    :param errors: The error list.
    :return: The error list after removing duplicates.
    """
    if not errors:
        return []

    # Build reverse mapping for quick lookup
    reverse_duplicates: Dict[Tuple[str, str], Tuple[str, str]] = {}
    for (src_linter, src_code), dup_set in DUPLICATES.items():
        for (dup_linter, dup_code) in dup_set:
            reverse_duplicates[(dup_linter, dup_code)] = (src_linter, src_code)

    # Track errors to keep
    seen: Set[Tuple[str, int, int, str]] = set()
    result: List[Error] = []

    for error in errors:
        # Create base key
        key = (error.filename, error.lnum, error.col, error.number)

        # Check if this error is a duplicate of something we've already seen
        is_duplicate = False
        error_key = (error.source, error.number)

        # Check if this error is marked as a duplicate of another
        if error_key in reverse_duplicates:
            original_key = reverse_duplicates[error_key]
            # Create a key with the original linter/code
            alt_key = (error.filename, error.lnum, error.col, original_key[1])
            if alt_key in seen:
                is_duplicate = True

        # Also check forward mapping
        if not is_duplicate and error_key in DUPLICATES:
            for (dup_linter, dup_code) in DUPLICATES[error_key]:
                alt_key = (error.filename, error.lnum, error.col, dup_code)
                if alt_key in seen:
                    is_duplicate = True
                    break

        if not is_duplicate and key not in seen:
            seen.add(key)
            result.append(error)

    return result


def filter_errors(
    errors: List[Error], select: Optional[List[str]] = None, ignore: Optional[List[str]] = None
) -> List[Error]:
    """Filter errors based on select and ignore patterns.

    :param errors: List of errors to filter
    :param select: List of error codes to select only (e.g., ["E301", "W503"])
    :param ignore: List of error codes to ignore
    :return: Filtered error list
    """
    if not select and not ignore:
        return errors

    result = []
    for error in errors:
        error_code = f"{error.type}{error.number}"

        # Apply select filter
        if select and error_code not in select:
            continue

        # Apply ignore filter
        if ignore and error_code in ignore:
            continue

        result.append(error)

    return result