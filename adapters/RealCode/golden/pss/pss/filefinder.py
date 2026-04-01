"""
File discovery module for intelligent source code search.
"""
import os
import fnmatch
from typing import List, Iterator, Optional

from .utils import istextfile


class FileFinder:
    """
    Recursively searches directories for files matching given criteria.

    Supports filtering by extension, filename patterns, text/binary detection,
    and inclusion/exclusion patterns.
    """

    def __init__(
        self,
        roots: List[str],
        recurse: bool = True,
        ignore_dirs: Optional[List[str]] = None,
        find_only_text_files: bool = False,
        search_extensions: Optional[List[str]] = None,
        ignore_extensions: Optional[List[str]] = None,
        search_patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        filter_include_patterns: Optional[List[str]] = None,
        filter_exclude_patterns: Optional[List[str]] = None,
    ):
        """
        Initialize FileFinder with search criteria.

        Args:
            roots: List of root directories to search
            recurse: Whether to search subdirectories (default True)
            ignore_dirs: Directory names to skip (e.g., '.git', '__pycache__')
            find_only_text_files: Only include files that pass text detection
            search_extensions: Include only files with these extensions (with dots)
            ignore_extensions: Exclude files with these extensions
            search_patterns: Include only files matching these shell patterns
            ignore_patterns: Exclude files matching these shell patterns
            filter_include_patterns: Include only paths matching these patterns
                (e.g., 'src/**')
            filter_exclude_patterns: Exclude paths matching these patterns
        """
        self.roots = [os.path.abspath(r) for r in roots]
        self.recurse = recurse
        self.ignore_dirs = set(ignore_dirs or [])
        self.find_only_text_files = find_only_text_files
        self.search_extensions = set(search_extensions or [])
        self.ignore_extensions = set(ignore_extensions or [])
        self.search_patterns = search_patterns or []
        self.ignore_patterns = ignore_patterns or []
        self.filter_include_patterns = filter_include_patterns or []
        self.filter_exclude_patterns = filter_exclude_patterns or []

    def files(self) -> Iterator[str]:
        """
        Generate file paths matching all criteria.

        Yields:
            Relative or absolute file paths (same as input root format)
        """
        for root in self.roots:
            # Determine if root path should be returned with original prefix
            # We'll keep the original root string for prefixing output paths
            original_root = root
            abs_root = os.path.abspath(root)

            if self.recurse:
                for dirpath, dirnames, filenames in os.walk(abs_root):
                    # Modify dirnames in-place to skip ignored directories
                    self._filter_directories(dirpath, dirnames)
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if self._should_include_file(filepath, abs_root, original_root):
                            yield self._make_output_path(filepath, abs_root, original_root)
            else:
                # Non-recursive: only examine files directly in root
                try:
                    entries = os.listdir(abs_root)
                except (OSError, PermissionError):
                    continue
                for entry in entries:
                    filepath = os.path.join(abs_root, entry)
                    if os.path.isfile(filepath):
                        if self._should_include_file(filepath, abs_root, original_root):
                            yield self._make_output_path(filepath, abs_root, original_root)

    def _filter_directories(self, dirpath: str, dirnames: List[str]) -> None:
        """
        Modify dirnames in-place to skip ignored directories.
        """
        # Remove directories that match ignore_dirs
        dirnames[:] = [
            d for d in dirnames
            if d not in self.ignore_dirs
        ]

    def _should_include_file(
        self,
        filepath: str,
        abs_root: str,
        original_root: str,
    ) -> bool:
        """
        Check if a file should be included based on all criteria.
        """
        # Convert to relative path for pattern matching
        rel_path = os.path.relpath(filepath, abs_root)

        # Check extension filters
        ext = os.path.splitext(filepath)[1]
        if self.search_extensions and ext not in self.search_extensions:
            return False
        if self.ignore_extensions and ext in self.ignore_extensions:
            return False

        # Check filename pattern filters
        filename = os.path.basename(filepath)
        if self.search_patterns and not any(
            fnmatch.fnmatch(filename, pat) for pat in self.search_patterns
        ):
            return False
        if self.ignore_patterns and any(
            fnmatch.fnmatch(filename, pat) for pat in self.ignore_patterns
        ):
            return False

        # Check path pattern filters (include/exclude)
        # Use forward slashes for pattern matching consistency
        pattern_path = rel_path.replace(os.sep, '/')
        if self.filter_include_patterns and not any(
            fnmatch.fnmatch(pattern_path, pat) for pat in self.filter_include_patterns
        ):
            return False
        if self.filter_exclude_patterns and any(
            fnmatch.fnmatch(pattern_path, pat) for pat in self.filter_exclude_patterns
        ):
            return False

        # Check text file detection
        if self.find_only_text_files:
            try:
                with open(filepath, 'rb') as f:
                    sample = f.read(512)
                if not istextfile(sample):
                    return False
            except (OSError, PermissionError):
                # If we can't read, assume not text
                return False

        return True

    def _make_output_path(
        self,
        filepath: str,
        abs_root: str,
        original_root: str,
    ) -> str:
        """
        Convert absolute filepath to output path using original root format.

        If original_root starts with './', we'll produce a relative path
        with the same prefix.
        """
        # Get relative path from absolute root
        rel_path = os.path.relpath(filepath, abs_root)

        # Reconstruct using original_root as base
        if original_root.endswith(os.sep) or original_root.endswith('/'):
            base = original_root.rstrip(os.sep).rstrip('/')
        else:
            base = original_root

        # Join with forward slash for consistency (os.path.join uses os.sep)
        if rel_path == '.':
            # File is the root itself (shouldn't happen for files)
            return base
        else:
            return os.path.join(base, rel_path)


if __name__ == '__main__':
    # Simple test
    finder = FileFinder(
        roots=['./test_data'],
        recurse=True,
        ignore_dirs=['.git', '__pycache__'],
        find_only_text_files=True,
        search_extensions=['.py', '.js'],
    )
    for f in finder.files():
        print(f)