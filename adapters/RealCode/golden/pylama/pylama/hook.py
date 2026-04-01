# -*- coding: utf-8 -*-
"""Git hook integration for Pylama."""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from pylama.config import parse_options
from pylama.core import run

LOGGER = logging.getLogger("pylama")


def git_hook(
    hook_type: str = "pre-commit",
    args: Optional[List[str]] = None,
    config: bool = True,
) -> int:
    """Run Pylama as a Git hook.

    Args:
        hook_type: Type of Git hook (currently only "pre-commit" supported)
        args: Additional command-line arguments
        config: Whether to load configuration file

    Returns:
        int: Exit code (0 = success, >0 = errors found)
    """
    if hook_type != "pre-commit":
        LOGGER.warning("Only pre-commit hooks are currently supported")
        return 1

    if args is None:
        args = []

    # Get staged Python files
    staged_files = _get_staged_python_files()
    if not staged_files:
        LOGGER.info("No staged Python files to check")
        return 0

    LOGGER.debug("Checking %d staged Python files", len(staged_files))

    # Parse options
    options = parse_options(args, config=config)

    # Override paths with staged files
    options.paths = staged_files

    # Run checks
    errors = run(options)

    # Output results
    if errors:
        print(f"Pylama found {len(errors)} issue(s) in staged files:")
        for error in errors:
            print(f"  {error.filename}:{error.lnum}:{error.col}: {error.source}: {error.text}")
        print("\nPlease fix the issues before committing.")
        return 1

    print("Pylama check passed - no issues found in staged files")
    return 0


def _get_staged_python_files() -> List[str]:
    """Get list of staged Python files from Git.

    Returns:
        List[str]: List of file paths
    """
    try:
        # Get staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )

        files = result.stdout.strip().splitlines()
        if not files:
            return []

        # Filter Python files
        python_files = []
        for file_path in files:
            if file_path.strip().endswith(".py"):
                # Check if file exists (it might have been deleted)
                if os.path.exists(file_path):
                    python_files.append(file_path)

        return python_files

    except subprocess.CalledProcessError as e:
        LOGGER.error("Failed to get staged files from Git: %s", e)
        return []
    except FileNotFoundError:
        LOGGER.error("Git not found. Is Git installed?")
        return []


def install_git_hook(
    hook_dir: Optional[Path] = None,
    overwrite: bool = False,
) -> bool:
    """Install Pylama as a Git pre-commit hook.

    Args:
        hook_dir: Directory where hooks are stored
                 (default: .git/hooks in current or parent directory)
        overwrite: Whether to overwrite existing hook

    Returns:
        bool: True if installation succeeded
    """
    # Find .git directory
    if hook_dir is None:
        git_dir = _find_git_dir()
        if not git_dir:
            LOGGER.error("Not a Git repository")
            return False
        hook_dir = git_dir / "hooks"

    if not hook_dir.exists():
        try:
            hook_dir.mkdir(parents=True)
        except Exception as e:
            LOGGER.error("Failed to create hooks directory: %s", e)
            return False

    hook_file = hook_dir / "pre-commit"

    # Check if hook already exists
    if hook_file.exists() and not overwrite:
        LOGGER.warning("Pre-commit hook already exists. Use --overwrite to replace.")
        return False

    # Create hook script
    hook_content = """#!/bin/sh
# Pylama pre-commit hook
# Automatically installed by pylama

pylama --git-hook "$@"
"""

    try:
        hook_file.write_text(hook_content, encoding="utf-8")
        hook_file.chmod(0o755)  # Make executable
        LOGGER.info("Installed Pylama pre-commit hook at %s", hook_file)
        return True
    except Exception as e:
        LOGGER.error("Failed to install hook: %s", e)
        return False


def _find_git_dir() -> Optional[Path]:
    """Find .git directory in current or parent directories.

    Returns:
        Optional[Path]: Path to .git directory or None if not found
    """
    current = Path.cwd()
    while current.parent != current:
        git_dir = current / ".git"
        if git_dir.exists():
            return git_dir
        current = current.parent

    return None


def main() -> int:
    """Command-line entry point for git-hook subcommand."""
    import argparse

    parser = argparse.ArgumentParser(description="Pylama Git hook integration")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Run hook command
    run_parser = subparsers.add_parser("run", help="Run Git hook")
    run_parser.add_argument(
        "--hook-type",
        default="pre-commit",
        choices=["pre-commit"],
        help="Type of Git hook",
    )
    run_parser.add_argument(
        "args",
        nargs="*",
        help="Additional arguments",
    )

    # Install command
    install_parser = subparsers.add_parser("install", help="Install Git hook")
    install_parser.add_argument(
        "--hook-dir",
        type=Path,
        help="Directory where hooks are stored",
    )
    install_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing hook",
    )

    args = parser.parse_args()

    if args.command == "run":
        return git_hook(args.hook_type, args.args)
    elif args.command == "install":
        success = install_git_hook(args.hook_dir, args.overwrite)
        return 0 if success else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())