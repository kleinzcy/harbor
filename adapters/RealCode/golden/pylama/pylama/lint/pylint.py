# -*- coding: utf-8 -*-
"""Pylint integration for Pylama."""

import logging
import tempfile
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    from pylint import lint
    HAS_PYLINT = True
except ImportError:
    HAS_PYLINT = False

from pylama.context import RunContext
from pylama.errors import Error as PylamaError
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")

if HAS_PYLINT:
    # Try to import TextReporter from various locations
    TextReporter = None
    try:
        from pylint.reporters.text import TextReporter
    except ImportError:
        try:
            from pylint.reporters import BaseReporter as TextReporter
        except ImportError:
            # If we can't import TextReporter, create a dummy class
            class DummyTextReporter:
                def __init__(self):
                    self.messages = []
            TextReporter = DummyTextReporter

    if TextReporter:
        class PylintJsonReporter(TextReporter):
            """Custom reporter to capture pylint messages as JSON."""

            name = "json"
            extension = "json"

            def __init__(self):
                """Initialize reporter."""
                self.messages = []
                try:
                    super().__init__()
                except TypeError:
                    # Some versions require output argument
                    pass

            def handle_message(self, msg):
                """Handle a pylint message."""
                self.messages.append({
                    "type": msg.category,
                    "module": msg.module,
                    "obj": msg.obj,
                    "line": msg.line,
                    "column": msg.column,
                    "path": msg.path,
                    "symbol": msg.symbol,
                    "message": msg.msg or "",
                    "message_id": msg.msg_id,
                })

            def _display(self, layout):
                """Override display to do nothing."""
                pass


class PylintLinter(LinterV2):
    """Pylint linter for Pylama."""

    name = "pylint"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add pylint-specific arguments."""
        if not HAS_PYLINT:
            return

        group = parser.add_argument_group("pylint options")
        group.add_argument(
            "--pylint-rcfile",
            default="",
            help="Specify a configuration file",
        )
        group.add_argument(
            "--pylint-disable",
            default="",
            help="Disable specific messages",
        )
        group.add_argument(
            "--pylint-enable",
            default="",
            help="Enable specific messages",
        )
        group.add_argument(
            "--pylint-reports",
            action="store_true",
            help="Enable output of reports",
        )
        group.add_argument(
            "--pylint-confidence",
            default="HIGH",
            help="Only show warnings with specified confidence levels",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[PylamaError]:
        """Run pylint check."""
        if not HAS_PYLINT:
            LOGGER.warning("pylint is not installed")
            return []

        # Check if PylintJsonReporter is available
        if not HAS_PYLINT or 'PylintJsonReporter' not in globals():
            LOGGER.debug("PylintJsonReporter not available")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Create arguments list
        args = self._create_args(params, str(ctx.filepath))

        # Create temporary file with content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(ctx.content)
            temp_path = f.name

        try:
            # Create reporter to capture messages
            reporter = PylintJsonReporter()

            # Run pylint
            # Note: We need to catch SystemExit from lint.Run
            import sys
            from io import StringIO

            # Capture stderr/stdout
            old_stderr = sys.stderr
            old_stdout = sys.stdout
            sys.stderr = StringIO()
            sys.stdout = StringIO()

            try:
                # Run pylint
                lint.Run([temp_path] + args, reporter=reporter, exit=False)
            except SystemExit:
                # pylint may call sys.exit(), ignore it
                pass
            finally:
                sys.stderr = old_stderr
                sys.stdout = old_stdout

            # Convert messages to errors
            errors: List[PylamaError] = []
            for msg in reporter.messages:
                # Skip if error should be ignored due to noqa comment
                if ctx.should_skip(msg["line"], msg["column"] - 1):  # column is 1-based
                    continue

                # Map pylint message type to our type
                msg_type = msg["type"]
                if msg_type == "error":
                    pylama_type = "E"
                elif msg_type == "fatal":
                    pylama_type = "E"
                elif msg_type == "warning":
                    pylama_type = "W"
                elif msg_type == "convention":
                    pylama_type = "C"
                elif msg_type == "refactor":
                    pylama_type = "R"
                else:
                    pylama_type = "W"

                error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=msg["line"],
                    col=msg["column"],
                    text=f"{msg['symbol']}: {msg['message']}",
                    number=msg["symbol"],
                    type=pylama_type,
                    source=self.name,
                )
                errors.append(error)

            return errors

        except Exception as e:
            LOGGER.warning("Pylint failed on %s: %s", ctx.filepath, e)
            return []
        finally:
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _create_args(self, params: dict, filename: str) -> List[str]:
        """Create pylint command line arguments."""
        args = []

        # Add rcfile if specified
        rcfile = params.get("pylint_rcfile", "")
        if rcfile:
            args.extend(["--rcfile", rcfile])

        # Add disable messages
        disable = params.get("pylint_disable", "")
        if disable:
            args.extend(["--disable", disable])

        # Add enable messages
        enable = params.get("pylint_enable", "")
        if enable:
            args.extend(["--enable", enable])

        # Add reports flag
        if params.get("pylint_reports"):
            args.append("--reports=y")

        # Add confidence
        confidence = params.get("pylint_confidence", "HIGH")
        if confidence:
            args.extend(["--confidence", confidence])

        # Disable score
        args.append("--score=n")

        # Use text format
        args.append("--output-format=text")

        return args


# Register linter
if HAS_PYLINT:
    PylintLinter()
else:
    LOGGER.warning("pylint is not available. Install with: pip install pylint")