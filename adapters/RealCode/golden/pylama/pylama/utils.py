# -*- coding: utf-8 -*-
"""Utility functions for Pylama."""

import fnmatch
import logging
import os
from pathlib import Path
from typing import List, Optional, Sequence

LOGGER = logging.getLogger("pylama")


def find_files(
    root: Path,
    patterns: Sequence[str] = ("*.py",),
    skip: Sequence[str] = (),
    exclude_hidden: bool = True,
) -> List[Path]:
    """Find files matching patterns in directory tree.

    Args:
        root: Root directory to search
        patterns: File patterns to match (e.g., ["*.py", "*.pyx"])
        skip: Patterns to skip (e.g., ["*.pyc", "test_*"])
        exclude_hidden: Whether to exclude hidden files/directories

    Returns:
        List[Path]: List of matching file paths
    """
    matching_files: List[Path] = []

    if not root.exists() or not root.is_dir():
        return matching_files

    # Convert patterns to lowercase for case-insensitive matching on Windows
    patterns_lower = [p.lower() for p in patterns] if os.name == "nt" else patterns
    skip_lower = [s.lower() for s in skip] if os.name == "nt" else skip

    for dirpath_str, dirnames, filenames in os.walk(str(root)):
        dirpath = Path(dirpath_str)

        # Filter directories
        dirnames[:] = [
            d for d in dirnames
            if not _should_skip_path(dirpath / d, skip_lower, exclude_hidden, is_dir=True)
        ]

        for filename in filenames:
            filepath = dirpath / filename

            # Check if file should be skipped
            if _should_skip_path(filepath, skip_lower, exclude_hidden, is_dir=False):
                continue

            # Check if file matches any pattern
            if _matches_patterns(filepath, patterns_lower):
                matching_files.append(filepath.resolve())

    return matching_files


def _should_skip_path(
    path: Path,
    skip_patterns: Sequence[str],
    exclude_hidden: bool,
    is_dir: bool,
) -> bool:
    """Check if path should be skipped.

    Args:
        path: Path to check
        skip_patterns: Patterns to skip
        exclude_hidden: Whether to exclude hidden paths
        is_dir: Whether path is a directory

    Returns:
        bool: True if path should be skipped
    """
    # Skip hidden files/directories
    if exclude_hidden and any(part.startswith(".") for part in path.parts):
        return True

    # Check skip patterns
    path_str = str(path)
    if os.name == "nt":
        path_str = path_str.lower()

    for pattern in skip_patterns:
        if fnmatch.fnmatch(path_str, pattern):
            return True
        if is_dir and fnmatch.fnmatch(path_str + "/*", pattern):
            return True

    return False


def _matches_patterns(path: Path, patterns: Sequence[str]) -> bool:
    """Check if path matches any of the patterns.

    Args:
        path: Path to check
        patterns: Patterns to match against

    Returns:
        bool: True if path matches any pattern
    """
    if not patterns:
        return True

    path_str = str(path)
    if os.name == "nt":
        path_str = path_str.lower()

    for pattern in patterns:
        if fnmatch.fnmatch(path_str, pattern):
            return True

    return False


def split_comma_separated(value: str) -> List[str]:
    """Split comma-separated string into list.

    Args:
        value: Comma-separated string

    Returns:
        List[str]: List of trimmed values
    """
    if not value:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


def normalize_path(path: str, rootdir: Optional[Path] = None) -> Path:
    """Normalize path to absolute Path object.

    Args:
        path: Path string
        rootdir: Root directory for relative paths

    Returns:
        Path: Normalized absolute path
    """
    path_obj = Path(path)

    if not path_obj.is_absolute():
        if rootdir:
            path_obj = rootdir / path_obj
        else:
            path_obj = path_obj.resolve()

    return path_obj


def is_python_file(path: Path) -> bool:
    """Check if file is a Python file.

    Args:
        path: Path to check

    Returns:
        bool: True if file has .py extension
    """
    return path.suffix.lower() == ".py"


def read_file_content(path: Path) -> Optional[str]:
    """Read file content with UTF-8 encoding.

    Args:
        path: Path to file

    Returns:
        Optional[str]: File content or None if reading fails
    """
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        LOGGER.warning("Failed to read file %s: %s", path, e)
        return None