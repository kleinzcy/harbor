# -*- coding: utf-8 -*-
"""Command-line interface and main entry points for Pylama."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Union

from pylama.config import DEFAULT_LINTERS, setup_logging
from pylama.core import run
from pylama.errors import Error
from pylama.lint import LINTERS

LOGGER = logging.getLogger("pylama")


def setup_parser() -> argparse.ArgumentParser:
    """Create argument parser for Pylama.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="pylama",
        description="Code audit tool for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pylama .                        # Check current directory
  pylama path/to/file.py          # Check specific file
  pylama -l pycodestyle,pyflakes  # Use specific linters
  pylama --format json            # Output in JSON format
  pylama --async                  # Process files asynchronously
        """,
    )

    # Path arguments
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to check (default: current directory)",
    )

    # Linter selection
    parser.add_argument(
        "-l", "--linters",
        default=",".join(DEFAULT_LINTERS),
        help="Comma-separated list of linters to use (default: %(default)s)",
    )

    # Output format
    parser.add_argument(
        "-f", "--format",
        choices=["json", "pycodestyle", "pylint", "parsable"],
        default="pycodestyle",
        help="Output format (default: %(default)s)",
    )

    # Filtering options
    parser.add_argument(
        "-i", "--ignore",
        default="",
        help="Comma-separated list of error codes to ignore",
    )

    parser.add_argument(
        "-s", "--select",
        default="",
        help="Comma-separated list of error codes to select (all others ignored)",
    )

    parser.add_argument(
        "--skip",
        default="",
        help="Comma-separated list of files/directories to skip",
    )

    # Configuration
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
    )

    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Do not load configuration file",
    )

    # Output options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode (only show errors)",
    )

    parser.add_argument(
        "--abspath",
        action="store_true",
        help="Show absolute paths in output",
    )

    parser.add_argument(
        "--sort",
        default="F,E,W,C,D",
        help="Sort errors by type (default: %(default)s)",
    )

    # Processing options
    parser.add_argument(
        "--async",
        dest="async_",
        action="store_true",
        help="Process files asynchronously",
    )

    parser.add_argument(
        "--concurrent",
        action="store_true",
        help="Process files concurrently (alias for --async)",
    )

    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=0,
        help="Number of parallel jobs (0 = auto)",
    )

    # Linter-specific options
    parser.add_argument(
        "--max-line-length",
        type=int,
        default=79,
        help="Maximum allowed line length",
    )

    parser.add_argument(
        "--max-complexity",
        type=int,
        default=10,
        help="Maximum McCabe complexity",
    )

    # Add arguments from registered linters
    for linter_name, linter_class in LINTERS.items():
        try:
            linter_class.add_args(parser)
        except Exception as e:
            LOGGER.debug("Failed to add args for linter %s: %s", linter_name, e)

    return parser


def parse_options(
    args: Optional[List[str]] = None,
    config: bool = True,
    rootdir: Optional[Path] = None,
    **overrides,
) -> argparse.Namespace:
    """Parse command-line arguments and configuration files.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        config: Whether to load configuration file
        rootdir: Root directory for config file search
        **overrides: Additional options to override

    Returns:
        argparse.Namespace: Parsed options
    """
    # Import here to avoid circular imports
    from pylama.config import parse_options as config_parse_options

    return config_parse_options(args, config, rootdir, **overrides)


def check_paths(
    paths: Union[str, Path, Sequence[Union[str, Path]]],
    options: Optional[argparse.Namespace] = None,
    rootdir: Optional[Path] = None,
) -> List[Error]:
    """Check code in specified paths.

    Args:
        paths: File or directory paths to check
        options: Configuration options
        rootdir: Root directory for relative paths

    Returns:
        List[Error]: List of errors found
    """
    if options is None:
        options = parse_options(config=False, rootdir=rootdir)

    if isinstance(paths, (str, Path)):
        paths = [paths]

    # Convert paths to strings
    path_strings = [str(p) for p in paths]

    # Update options with paths
    options.paths = path_strings

    # Run checks
    errors = run(options)

    return errors


def shell(args: Optional[List[str]] = None) -> int:
    """Command-line shell interface.

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code (0 = success, >0 = errors found)
    """
    # Parse options
    options = parse_options(args)

    # Setup logging
    setup_logging(options.verbose)

    # Run checks
    errors = run(options)

    # Output results
    if options.format == "json":
        import json
        error_dicts = [
            {
                "filename": e.filename,
                "lnum": e.lnum,
                "col": e.col,
                "text": e.text,
                "type": e.type,
                "source": e.source,
                "number": e.number,
            }
            for e in errors
        ]
        print(json.dumps(error_dicts, indent=2))
    elif options.format == "pycodestyle":
        for error in errors:
            print(f"{error.filename}:{error.lnum}:{error.col}: {error.number} {error.text}")
    elif options.format == "pylint":
        for error in errors:
            print(f"{error.filename}:{error.lnum}: [{error.source}] {error.text}")
    elif options.format == "parsable":
        for error in errors:
            print(f"{error.filename}:{error.lnum}:{error.col}:{error.source}:{error.number}: {error.text}")

    # Return exit code
    return 1 if errors else 0


def main() -> int:
    """Main entry point for command-line tool."""
    return shell()


if __name__ == "__main__":
    sys.exit(main())