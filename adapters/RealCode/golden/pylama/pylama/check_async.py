# -*- coding: utf-8 -*-
"""Asynchronous/concurrent checking for Pylama."""

import concurrent.futures
import logging
import os
from argparse import Namespace
from pathlib import Path
from typing import List, Optional

from pylama.core import _check_file
from pylama.errors import Error

LOGGER = logging.getLogger("pylama")


def check_async(
    files: List[Path],
    linters: List,
    options: Namespace,
    max_workers: Optional[int] = None,
) -> List[Error]:
    """Check files asynchronously/concurrently.

    Args:
        files: List of file paths to check
        linters: List of linter instances
        options: Configuration options
        max_workers: Maximum number of worker processes/threads
                    (default: auto-detect based on CPU count)

    Returns:
        List[Error]: Combined list of errors from all files
    """
    if not files:
        return []

    # Determine number of workers
    if max_workers is None or max_workers <= 0:
        # Use CPU count, but limit to number of files
        cpu_count = os.cpu_count() or 1
        max_workers = min(cpu_count, len(files))

    LOGGER.debug("Using %d workers for async processing", max_workers)

    all_errors: List[Error] = []

    # Use ThreadPoolExecutor for I/O bound tasks (file reading)
    # For CPU-bound linters, ProcessPoolExecutor might be better,
    # but linters often have initialization overhead.
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks
        future_to_file = {
            executor.submit(_check_file_async, filepath, linters, options): filepath
            for filepath in files
        }

        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            filepath = future_to_file[future]
            try:
                errors = future.result(timeout=300)  # 5 minute timeout per file
                all_errors.extend(errors)
                LOGGER.debug("Completed async check for %s (%d errors)", filepath, len(errors))
            except concurrent.futures.TimeoutError:
                LOGGER.warning("Timeout checking file: %s", filepath)
            except Exception as e:
                LOGGER.warning("Error checking file %s: %s", filepath, e)

    return all_errors


def _check_file_async(
    filepath: Path,
    linters: List,
    options: Namespace,
) -> List[Error]:
    """Check a single file (wrapper for async execution).

    Args:
        filepath: Path to file
        linters: List of linter instances
        options: Configuration options

    Returns:
        List[Error]: List of errors found in file
    """
    # This is a thin wrapper around _check_file to make it compatible
    # with concurrent execution
    return _check_file(filepath, linters, options)


def check_async_wrapper(options: Namespace) -> List[Error]:
    """Convenience wrapper for async checking from command line.

    Args:
        options: Configuration options

    Returns:
        List[Error]: List of errors found
    """
    # This function is imported in main.py as check_async
    from pylama.core import run

    # Override options to force async processing
    options.async_ = True
    options.concurrent = True

    return run(options)