# -*- coding: utf-8 -*-
"""Core checking engine for Pylama."""

import logging
from argparse import Namespace
from pathlib import Path
from typing import List, Set

from pylama.config import setup_logging
from pylama.context import RunContext
from pylama.errors import Error, remove_duplicates
from pylama.lint import get_linter
from pylama.utils import find_files

LOGGER = logging.getLogger("pylama")


def run(options: Namespace) -> List[Error]:
    """Run code checks with given options.

    Args:
        options: Configuration options

    Returns:
        List[Error]: List of errors found
    """
    # Setup logging
    setup_logging(options.verbose)

    LOGGER.debug("Starting code audit with options: %s", options)

    # Parse linter list
    linter_names = _parse_linter_list(options.linters)
    LOGGER.debug("Using linters: %s", linter_names)

    # Get linter instances
    linters = []
    for name in linter_names:
        linter_class = get_linter(name)
        if linter_class:
            try:
                linter = linter_class()
                linters.append(linter)
            except Exception as e:
                LOGGER.warning("Failed to instantiate linter %s: %s", name, e)
        else:
            LOGGER.warning("Unknown linter: %s", name)

    if not linters:
        LOGGER.error("No valid linters available")
        return []

    # Find files to check
    files = _find_files_to_check(options.paths, options.skip)
    LOGGER.debug("Found %d files to check", len(files))

    # Filter files based on linter capabilities
    files = [f for f in files if _should_check_file(f, linters)]
    LOGGER.debug("After filtering: %d files to check", len(files))

    # Process files
    all_errors: List[Error] = []

    if getattr(options, "async_", False) or getattr(options, "concurrent", False):
        # Async processing
        from pylama.check_async import check_async
        all_errors = check_async(files, linters, options)
    else:
        # Sync processing
        for filepath in files:
            errors = _check_file(filepath, linters, options)
            all_errors.extend(errors)

    # Apply filters
    all_errors = _filter_errors(all_errors, options)

    # Sort errors
    all_errors = _sort_errors(all_errors, options)

    # Remove duplicates
    all_errors = remove_duplicates(all_errors)

    LOGGER.debug("Found %d errors", len(all_errors))
    return all_errors


def _parse_linter_list(linters_str) -> List[str]:
    """Parse linter list.

    Args:
        linters_str: Comma-separated string or list of linter names

    Returns:
        List[str]: List of linter names
    """
    if not linters_str:
        return []

    if isinstance(linters_str, list):
        return [name.strip() for name in linters_str if name.strip()]

    # Assume it's a string
    return [name.strip() for name in linters_str.split(",") if name.strip()]


def _find_files_to_check(paths: List[str], skip_patterns: str) -> List[Path]:
    """Find all files to check.

    Args:
        paths: List of paths to check
        skip_patterns: Comma-separated patterns to skip

    Returns:
        List[Path]: List of file paths to check
    """
    all_files: List[Path] = []

    skip_list = []
    if skip_patterns:
        skip_list = [p.strip() for p in skip_patterns.split(",") if p.strip()]

    for path_str in paths:
        path = Path(path_str)

        if not path.exists():
            LOGGER.warning("Path does not exist: %s", path)
            continue

        if path.is_file():
            all_files.append(path.resolve())
        elif path.is_dir():
            files = find_files(
                path,
                patterns=["*.py"],
                skip=skip_list,
                exclude_hidden=True,
            )
            all_files.extend(files)

    # Remove duplicates
    unique_files = list(set(all_files))

    return unique_files


def _should_check_file(filepath: Path, linters: List) -> bool:
    """Check if file should be checked by any linter.

    Args:
        filepath: Path to file
        linters: List of linter instances

    Returns:
        bool: True if file should be checked
    """
    for linter in linters:
        if linter.allow(filepath):
            return True
    return False


def _check_file(
    filepath: Path,
    linters: List,
    options: Namespace,
) -> List[Error]:
    """Check a single file with all linters.

    Args:
        filepath: Path to file
        linters: List of linter instances
        options: Configuration options

    Returns:
        List[Error]: List of errors found in file
    """
    LOGGER.debug("Checking file: %s", filepath)

    # Read file content
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        LOGGER.warning("Failed to read file %s: %s", filepath, e)
        return []

    # Create context
    ctx = RunContext(filepath, content, options)

    # Run linters
    all_errors: List[Error] = []

    for linter in linters:
        if not linter.allow(filepath):
            continue

        try:
            errors = linter.run_check(ctx)
            LOGGER.debug("Linter %s found %d errors in %s", linter.name, len(errors), filepath)
            all_errors.extend(errors)
        except Exception as e:
            LOGGER.warning("Linter %s failed on file %s: %s", linter.name, filepath, e)

    return all_errors


def _filter_errors(errors: List[Error], options: Namespace) -> List[Error]:
    """Filter errors based on ignore/select options.

    Args:
        errors: List of errors
        options: Configuration options

    Returns:
        List[Error]: Filtered list of errors
    """
    # Parse ignore patterns
    ignore_codes: Set[str] = set()
    if hasattr(options, "ignore") and options.ignore:
        if isinstance(options.ignore, list):
            ignore_codes.update(code.strip() for code in options.ignore if code.strip())
        else:
            ignore_codes.update(code.strip() for code in options.ignore.split(",") if code.strip())

    # Parse select patterns
    select_codes: Set[str] = set()
    if hasattr(options, "select") and options.select:
        if isinstance(options.select, list):
            select_codes.update(code.strip() for code in options.select if code.strip())
        else:
            select_codes.update(code.strip() for code in options.select.split(",") if code.strip())

    filtered_errors = []

    for error in errors:
        error_code = error.number

        # Apply ignore filter
        if error_code in ignore_codes:
            continue

        # Apply select filter
        if select_codes and error_code not in select_codes:
            continue

        filtered_errors.append(error)

    return filtered_errors


def _sort_errors(errors: List[Error], options: Namespace) -> List[Error]:
    """Sort errors according to options.

    Args:
        errors: List of errors
        options: Configuration options

    Returns:
        List[Error]: Sorted list of errors
    """
    if not errors:
        return errors

    # Parse sort order
    sort_order = "F,E,W,C,D"
    if hasattr(options, "sort") and options.sort:
        sort_order = options.sort

    # Create mapping of error types to sort order
    type_order = {}
    for i, type_char in enumerate(sort_order.split(",")):
        type_order[type_char.strip()] = i

    def error_key(error: Error) -> tuple:
        """Sort key for errors."""
        # First by type order
        type_idx = type_order.get(error.type, 999)
        # Then by filename
        filename = error.filename
        # Then by line number
        line = error.lnum
        # Then by column
        col = error.col

        return (type_idx, filename, line, col)

    return sorted(errors, key=error_key)


# For backward compatibility
check_paths = run