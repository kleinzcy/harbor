# -*- coding: utf-8 -*-
"""Pytest plugin for Pylama."""

import logging
from pathlib import Path
from typing import List

import pytest

from pylama.core import run
from pylama.errors import Error

LOGGER = logging.getLogger("pylama")


def pytest_addoption(parser):
    """Add Pylama options to pytest."""
    group = parser.getgroup("pylama", "Code quality checking with Pylama")
    group.addoption(
        "--pylama",
        action="store_true",
        default=False,
        help="Run Pylama code quality checks",
    )
    group.addoption(
        "--pylama-linters",
        default="pycodestyle,pyflakes,mccabe",
        help="Comma-separated list of linters to use",
    )
    group.addoption(
        "--pylama-ignore",
        default="",
        help="Comma-separated list of error codes to ignore",
    )
    group.addoption(
        "--pylama-select",
        default="",
        help="Comma-separated list of error codes to select",
    )
    group.addoption(
        "--pylama-max-line-length",
        type=int,
        default=79,
        help="Maximum allowed line length",
    )
    group.addoption(
        "--pylama-max-complexity",
        type=int,
        default=10,
        help="Maximum McCabe complexity",
    )


def pytest_configure(config):
    """Configure Pylama plugin."""
    if config.getoption("--pylama"):
        # Register our marker
        config.addinivalue_line(
            "markers",
            "pylama: mark test to run Pylama checks on specific paths",
        )


def pytest_collect_file(file_path: Path, parent):
    """Collect Pylama test items."""
    if not parent.config.getoption("--pylama"):
        return None

    # Only check Python files
    if file_path.suffix != ".py":
        return None

    # Skip test files by default (they're checked by other tests)
    if file_path.name.startswith("test_") or file_path.name.endswith("_test.py"):
        return None

    # Create PylamaItem for each Python file
    return PylamaItem.from_parent(parent, path=file_path)


class PylamaError(Exception):
    """Exception raised when Pylama finds errors."""

    def __init__(self, errors: List[Error]):
        self.errors = errors
        super().__init__(f"Pylama found {len(errors)} code quality issue(s)")


class PylamaItem(pytest.Item):
    """Pytest item representing a Pylama check."""

    def __init__(self, path: Path, **kwargs):
        super().__init__(name=f"pylama::{path}", **kwargs)
        self.path = path

    def runtest(self):
        """Run Pylama check on the file."""
        # Get options from pytest config
        config = self.config

        # Build options namespace
        class Options:
            pass

        options = Options()
        options.linters = config.getoption("--pylama-linters")
        options.ignore = config.getoption("--pylama-ignore")
        options.select = config.getoption("--pylama-select")
        options.max_line_length = config.getoption("--pylama-max-line-length")
        options.max_complexity = config.getoption("--pylama-max-complexity")
        options.paths = [str(self.path)]
        options.skip = ""
        options.verbose = config.getoption("verbose") > 0
        options.async_ = False
        options.concurrent = False
        options.sort = "F,E,W,C,D"
        options.format = "pycodestyle"
        options.abspath = False

        # Run Pylama
        errors = run(options)

        if errors:
            raise PylamaError(errors)

    def repr_failure(self, excinfo):
        """Format failure representation."""
        if excinfo.errisinstance(PylamaError):
            errors = excinfo.value.errors
            message = [f"Pylama found {len(errors)} issue(s) in {self.path}:"]
            for error in errors[:10]:  # Show first 10 errors
                message.append(
                    f"  Line {error.lnum}, Col {error.col}: "
                    f"[{error.source}] {error.number}: {error.text}"
                )
            if len(errors) > 10:
                message.append(f"  ... and {len(errors) - 10} more issue(s)")
            return "\n".join(message)
        return super().repr_failure(excinfo)

    def reportinfo(self):
        """Report information about this test item."""
        return (self.path, 0, f"Pylama check: {self.path}")


@pytest.fixture
def pylama_check(request):
    """Fixture to run Pylama checks in tests.

    Example:
        def test_my_code(pylama_check):
            errors = pylama_check("my_module.py")
            assert len(errors) == 0
    """

    def check_paths(paths, **kwargs):
        """Check paths with Pylama.

        Args:
            paths: File or directory paths to check
            **kwargs: Pylama options

        Returns:
            List[Error]: List of errors found
        """
        # Get default options from pytest config
        config = request.config

        class Options:
            pass

        options = Options()
        options.linters = kwargs.get("linters", config.getoption("--pylama-linters"))
        options.ignore = kwargs.get("ignore", config.getoption("--pylama-ignore"))
        options.select = kwargs.get("select", config.getoption("--pylama-select"))
        options.max_line_length = kwargs.get(
            "max_line_length",
            config.getoption("--pylama-max-line-length"),
        )
        options.max_complexity = kwargs.get(
            "max_complexity",
            config.getoption("--pylama-max-complexity"),
        )
        options.paths = [paths] if isinstance(paths, (str, Path)) else list(paths)
        options.skip = kwargs.get("skip", "")
        options.verbose = kwargs.get("verbose", config.getoption("verbose") > 0)
        options.async_ = kwargs.get("async_", False)
        options.concurrent = kwargs.get("concurrent", False)
        options.sort = kwargs.get("sort", "F,E,W,C,D")
        options.format = kwargs.get("format", "pycodestyle")
        options.abspath = kwargs.get("abspath", False)

        return run(options)

    return check_paths