# -*- coding: utf-8 -*-
"""Mypy integration for Pylama."""

import logging
import tempfile
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    from mypy import api as mypy_api
    HAS_MYPY = True
except ImportError:
    HAS_MYPY = False

from pylama.context import RunContext
from pylama.errors import Error as PylamaError
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class MypyLinter(LinterV2):
    """Mypy linter for Pylama."""

    name = "mypy"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add mypy-specific arguments."""
        if not HAS_MYPY:
            return

        group = parser.add_argument_group("mypy options")
        group.add_argument(
            "--mypy-config",
            default="",
            help="Path to mypy configuration file",
        )
        group.add_argument(
            "--mypy-python-version",
            default="",
            help="Type check Python version (e.g., 3.8)",
        )
        group.add_argument(
            "--mypy-strict",
            action="store_true",
            help="Enable strict mode",
        )
        group.add_argument(
            "--mypy-ignore-missing-imports",
            action="store_true",
            help="Ignore missing imports",
        )
        group.add_argument(
            "--mypy-disallow-untyped-defs",
            action="store_true",
            help="Disallow untyped function definitions",
        )
        group.add_argument(
            "--mypy-disallow-incomplete-defs",
            action="store_true",
            help="Disallow incomplete type annotations",
        )
        group.add_argument(
            "--mypy-warn-return-any",
            action="store_true",
            help="Warn if function returns Any",
        )
        group.add_argument(
            "--mypy-warn-unused-ignores",
            action="store_true",
            help="Warn about unused type: ignore comments",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[PylamaError]:
        """Run mypy check."""
        if not HAS_MYPY:
            LOGGER.warning("mypy is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Create arguments list
        args = self._create_args(params)

        # Create temporary file with content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(ctx.content)
            temp_path = f.name

        try:
            # Run mypy on the file
            # mypy.api.run returns (stdout, stderr, exit_code)
            result = mypy_api.run([temp_path] + args)

            stdout, stderr, exit_code = result

            # Parse mypy output
            errors = self._parse_mypy_output(stdout, ctx)

            # Log any errors from stderr
            if stderr:
                LOGGER.debug("Mypy stderr: %s", stderr)

            return errors

        except Exception as e:
            LOGGER.warning("Mypy failed on %s: %s", ctx.filepath, e)
            return []
        finally:
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _create_args(self, params: dict) -> List[str]:
        """Create mypy command line arguments."""
        args = []

        # Add config file if specified
        config = params.get("mypy_config", "")
        if config:
            args.extend(["--config-file", config])

        # Add Python version
        python_version = params.get("mypy_python_version", "")
        if python_version:
            args.extend(["--python-version", python_version])

        # Add strict mode
        if params.get("mypy_strict"):
            args.append("--strict")

        # Add ignore missing imports
        if params.get("mypy_ignore_missing_imports"):
            args.append("--ignore-missing-imports")

        # Add disallow untyped defs
        if params.get("mypy_disallow_untyped_defs"):
            args.append("--disallow-untyped-defs")

        # Add disallow incomplete defs
        if params.get("mypy_disallow_incomplete_defs"):
            args.append("--disallow-incomplete-defs")

        # Add warn return any
        if params.get("mypy_warn_return_any"):
            args.append("--warn-return-any")

        # Add warn unused ignores
        if params.get("mypy_warn_unused_ignores"):
            args.append("--warn-unused-ignores")

        # Add other common options
        args.append("--show-error-codes")  # Show error codes
        args.append("--no-error-summary")  # Don't show error summary
        args.append("--no-pretty")  # Don't use pretty output

        return args

    def _parse_mypy_output(self, output: str, ctx: RunContext) -> List[PylamaError]:
        """Parse mypy output into Pylama errors."""
        errors: List[PylamaError] = []

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            # Parse mypy output format: filename:line:col: type: message [error-code]
            # Example: test.py:10:5: error: Incompatible types in assignment (expression has type "str", variable has type "int") [assignment]
            if line.startswith(str(ctx.filepath) + ":"):
                # Remove filename prefix
                remaining = line[len(str(ctx.filepath)) + 1:]

                # Split by colon
                parts = remaining.split(":", 3)
                if len(parts) >= 4:
                    lineno_str, col_str, severity, message = parts[0], parts[1], parts[2].strip(), parts[3].strip()

                    # Extract error code if present
                    error_code = ""
                    if "[" in message and "]" in message:
                        start = message.rfind("[")
                        end = message.rfind("]")
                        if start != -1 and end != -1 and start < end:
                            error_code = message[start + 1:end]
                            message = message[:start].strip()

                    # Convert line and column numbers
                    try:
                        lineno = int(lineno_str)
                        col = int(col_str) if col_str else 1
                    except ValueError:
                        continue

                    # Skip if error should be ignored due to noqa comment
                    if ctx.should_skip(lineno, col - 1):  # col is 1-based
                        continue

                    # Map mypy severity to our type
                    if severity == "error":
                        pylama_type = "E"
                    elif severity == "warning":
                        pylama_type = "W"
                    elif severity == "note":
                        pylama_type = "I"
                    else:
                        pylama_type = "E"

                    # Use error code if available, otherwise use generic
                    if not error_code:
                        error_code = "mypy"

                    error = PylamaError(
                        filename=str(ctx.filepath),
                        lnum=lineno,
                        col=col,
                        text=message,
                        number=error_code,
                        type=pylama_type,
                        source=self.name,
                    )
                    errors.append(error)

        return errors


# Register linter
if HAS_MYPY:
    MypyLinter()
else:
    LOGGER.warning("mypy is not available. Install with: pip install mypy")