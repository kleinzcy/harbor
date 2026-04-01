# -*- coding: utf-8 -*-
"""Pyflakes integration for Pylama."""

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    from pyflakes import api as pyflakes_api
    from pyflakes import reporter as pyflakes_reporter
    HAS_PYFLAKES = True
except ImportError:
    HAS_PYFLAKES = False

from pylama.context import RunContext
from pylama.errors import Error
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


if HAS_PYFLAKES:
    class PyflakesReporter(pyflakes_reporter.Reporter):
        """Custom reporter to collect pyflakes messages."""

        def __init__(self):
            super().__init__(sys.stdout, sys.stderr)
            self.messages = []

        def unexpectedError(self, filename, msg):
            """Handle unexpected errors."""
            self.messages.append(("error", filename, 0, 0, str(msg)))

        def syntaxError(self, filename, msg, lineno, offset, text):
            """Handle syntax errors."""
            self.messages.append(("syntax", filename, lineno, offset, str(msg)))

        def flake(self, message):
            """Handle flake messages."""
            self.messages.append(("flake", message.filename, message.lineno, message.col, str(message)))
else:
    # Dummy class when pyflakes is not available
    class PyflakesReporter:
        pass


class PyflakesLinter(LinterV2):
    """Pyflakes linter for Pylama."""

    name = "pyflakes"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add pyflakes-specific arguments."""
        if not HAS_PYFLAKES:
            return

        group = parser.add_argument_group("pyflakes options")
        group.add_argument(
            "--pyflakes-builtins",
            default="",
            help="Comma-separated list of builtins to ignore",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[Error]:
        """Run pyflakes check."""
        if not HAS_PYFLAKES:
            LOGGER.warning("pyflakes is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Create custom reporter
        reporter = PyflakesReporter()

        try:
            # Check the code
            # Note: pyflakes.api.check signature is check(code, filename, reporter)
            warnings = pyflakes_api.check(
                ctx.content,
                str(ctx.filepath),
                reporter,
            )
        except SyntaxError as e:
            # Handle syntax errors
            return self._handle_syntax_error(e, ctx)

        except Exception as e:
            LOGGER.warning("Pyflakes failed on %s: %s", ctx.filepath, e)
            return []

        # Convert messages to errors
        errors: List[Error] = []
        for msg_type, filename, lineno, offset, text in reporter.messages:
            # Skip if error should be ignored due to noqa comment
            if lineno > 0 and ctx.should_skip(lineno, offset):
                continue

            error = Error(
                filename=str(ctx.filepath),
                lnum=lineno,
                col=offset + 1,  # pyflakes uses 0-based, we use 1-based
                text=self._clean_message(text),
                number=self._get_error_code(msg_type, text),
                type="W",  # Pyflakes reports warnings
                source=self.name,
            )
            errors.append(error)

        return errors

    def _get_builtins(self, params: dict) -> set:
        """Get builtins to ignore from parameters."""
        builtins_str = params.get("pyflakes_builtins", "")
        if not builtins_str:
            return set()

        return set(b.strip() for b in builtins_str.split(",") if b.strip())

    def _handle_syntax_error(self, error: SyntaxError, ctx: RunContext) -> List[Error]:
        """Handle syntax errors from pyflakes."""
        errors = []

        # Try to extract line number from exception
        lineno = getattr(error, "lineno", 1)
        offset = getattr(error, "offset", 0)
        text = str(error.msg) if hasattr(error, "msg") else str(error)

        error_obj = Error(
            filename=str(ctx.filepath),
            lnum=lineno,
            col=offset + 1,
            text=text,
            number="E999",  # Generic syntax error code
            type="E",  # Syntax errors are errors
            source=self.name,
        )
        errors.append(error_obj)

        return errors

    def _clean_message(self, text: str) -> str:
        """Clean pyflakes message text."""
        # Remove trailing newlines
        text = text.strip()

        # Remove filename prefix if present
        if "'" in text and ":" in text:
            # Format: "filename.py: line message"
            parts = text.split(":", 2)
            if len(parts) >= 3:
                text = parts[2].strip()

        return text

    def _get_error_code(self, msg_type: str, text: str) -> str:
        """Extract error code from pyflakes message."""
        # Pyflakes doesn't have error codes, so we create some based on message type
        if msg_type == "syntax":
            return "E999"
        elif msg_type == "error":
            return "E998"
        else:
            # Try to extract code from message
            if "' is not defined" in text:
                return "F821"  # Undefined name
            elif "imported but unused" in text:
                return "F401"  # Unused import
            elif "' imported but unused" in text:
                return "F401"  # Unused import
            elif "redefinition of unused" in text:
                return "F811"  # Redefinition of unused
            elif "assigned to but never used" in text:
                return "F841"  # Unused variable
            elif "undefined name" in text:
                return "F821"  # Undefined name
            else:
                return "F000"  # Generic pyflakes warning


# Register linter
if HAS_PYFLAKES:
    PyflakesLinter()
else:
    LOGGER.warning("pyflakes is not available. Install with: pip install pyflakes")