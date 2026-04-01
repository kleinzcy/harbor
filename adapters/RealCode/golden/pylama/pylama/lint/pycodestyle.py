# -*- coding: utf-8 -*-
"""Pycodestyle (formerly pep8) integration for Pylama."""

import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    import pycodestyle
    HAS_PYCODESTYLE = True
except ImportError:
    HAS_PYCODESTYLE = False

from pylama.context import RunContext
from pylama.errors import Error
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class PycodestyleLinter(LinterV2):
    """Pycodestyle linter for Pylama."""

    name = "pycodestyle"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add pycodestyle-specific arguments."""
        if not HAS_PYCODESTYLE:
            return

        group = parser.add_argument_group("pycodestyle options")
        group.add_argument(
            "--max-line-length",
            type=int,
            default=79,
            help="Maximum allowed line length",
        )
        group.add_argument(
            "--ignore",
            default="",
            help="Comma-separated list of error codes to ignore",
        )
        group.add_argument(
            "--select",
            default="",
            help="Comma-separated list of error codes to select",
        )
        group.add_argument(
            "--hang-closing",
            action="store_true",
            help="Hang closing bracket instead of matching indentation",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[Error]:
        """Run pycodestyle check."""
        if not HAS_PYCODESTYLE:
            LOGGER.warning("pycodestyle is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Create options
        options = self._create_options(params)

        # Use StringIO to capture output

        # Create a custom reporter that collects errors
        class ErrorCollector:
            def __init__(self):
                self.errors = []

            def __call__(self, line_number, offset, code, text, check=None, line=None):
                # line_number, offset are 0-based
                # code is like 'E225', text is full message
                self.errors.append((line_number + 1, offset, code, text))

        # Create error collector
        collector = ErrorCollector()

        # Monkey-patch the reporter's error method
        original_error = pycodestyle.BaseReport.error
        def patched_error(self, line_number, offset, text, check):
            # Extract code from text (text format: "E225 missing whitespace around operator")
            parts = text.split(' ', 1)
            code = parts[0] if parts else ""
            collector(line_number, offset, code, text)
            return original_error(self, line_number, offset, text, check)

        # Temporarily patch
        pycodestyle.BaseReport.error = patched_error

        try:
            # Create a temporary file to check
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(ctx.content)
                temp_path = f.name

            try:
                # Run pycodestyle on the file
                # Create style guide with minimal arguments
                style_guide = pycodestyle.StyleGuide(
                    paths=[temp_path],
                    reporter=pycodestyle.StandardReport,
                )
                # Update options with our custom settings
                for key, value in vars(options).items():
                    if hasattr(style_guide.options, key):
                        setattr(style_guide.options, key, value)
                # This will trigger our patched error method
                style_guide.check_files()
            finally:
                import os
                os.unlink(temp_path)

        except Exception as e:
            LOGGER.warning("PycodeStyle failed on %s: %s", ctx.filepath, e)
            return []
        finally:
            # Restore original method
            pycodestyle.BaseReport.error = original_error

        # Convert collected errors to Pylama errors
        errors: List[Error] = []
        for lineno, offset, code, text in collector.errors:
            # Skip if error should be ignored due to noqa comment
            if ctx.should_skip(lineno, offset):
                continue

            error = Error(
                filename=str(ctx.filepath),
                lnum=lineno,
                col=offset + 1,  # pycodestyle uses 0-based, we use 1-based
                text=text,
                number=code,
                type=self._get_error_type(code),
                source=self.name,
            )
            errors.append(error)

        return errors

    def _create_options(self, params: dict):
        """Create pycodestyle options from parameters."""
        # Get default options from a StyleGuide
        style_guide = pycodestyle.StyleGuide(
            paths=[],  # We'll check files directly
            reporter=pycodestyle.StandardReport,
        )
        options = style_guide.options

        # Set max line length
        if "max_line_length" in params:
            options.max_line_length = int(params["max_line_length"])

        # Set ignore patterns
        if "ignore" in params and params["ignore"]:
            if isinstance(params["ignore"], list):
                options.ignore = set(params["ignore"])
            else:
                options.ignore = set(params["ignore"].split(","))

        # Set select patterns
        if "select" in params and params["select"]:
            if isinstance(params["select"], list):
                options.select = set(params["select"])
            else:
                options.select = set(params["select"].split(","))

        # Set other options
        if params.get("hang_closing"):
            options.hang_closing = True

        # Return the options object
        return options

    def _get_error_type(self, code: str) -> str:
        """Map pycodestyle error code to type."""
        if code.startswith("E"):
            return "E"  # Error
        elif code.startswith("W"):
            return "W"  # Warning
        else:
            return "E"  # Default to error


# Register linter
if HAS_PYCODESTYLE:
    PycodestyleLinter()
else:
    LOGGER.warning("pycodestyle is not available. Install with: pip install pycodestyle")