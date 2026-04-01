# -*- coding: utf-8 -*-
"""McCabe complexity checker integration for Pylama."""

import ast
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    import mccabe
    HAS_MCCABE = True
except ImportError:
    HAS_MCCABE = False

from pylama.context import RunContext
from pylama.errors import Error
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class McCabeLinter(LinterV2):
    """McCabe complexity checker for Pylama."""

    name = "mccabe"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add mccabe-specific arguments."""
        if not HAS_MCCABE:
            return

        group = parser.add_argument_group("mccabe options")
        group.add_argument(
            "--max-complexity",
            type=int,
            default=10,
            help="Maximum McCabe cyclomatic complexity",
        )
        group.add_argument(
            "--mccabe-ignore",
            default="",
            help="Comma-separated list of function names to ignore",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[Error]:
        """Run mccabe complexity check."""
        if not HAS_MCCABE:
            LOGGER.warning("mccabe is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)
        max_complexity = params.get("max_complexity", 10)
        ignore_names = self._parse_ignore_list(params.get("mccabe_ignore", ""))

        try:
            # Parse AST
            tree = ast.parse(ctx.content, str(ctx.filepath))
        except SyntaxError as e:
            # Syntax error - can't check complexity
            LOGGER.debug("Syntax error in %s: %s", ctx.filepath, e)
            return []

        # Create checker
        checker = mccabe.McCabeChecker(tree, str(ctx.filepath))
        checker.max_complexity = max_complexity

        # Check complexity
        errors: List[Error] = []
        for lineno, offset, text, _ in checker.run():
            # Skip if error should be ignored due to noqa comment
            if ctx.should_skip(lineno, offset):
                continue

            # Extract function name from message
            func_name = self._extract_function_name(text)

            # Check if function is in ignore list
            if func_name and func_name in ignore_names:
                continue

            error = Error(
                filename=str(ctx.filepath),
                lnum=lineno,
                col=offset + 1,
                text=text,
                number="C901",  # McCabe complexity error code
                type="C",  # Complexity
                source=self.name,
            )
            errors.append(error)

        return errors

    def _parse_ignore_list(self, ignore_str: str) -> set:
        """Parse comma-separated ignore list.

        Args:
            ignore_str: Comma-separated list of function names

        Returns:
            set: Set of function names to ignore
        """
        if not ignore_str:
            return set()

        return {name.strip() for name in ignore_str.split(",") if name.strip()}

    def _extract_function_name(self, text: str) -> str:
        """Extract function name from mccabe message.

        Args:
            text: Message text like "'function_name' is too complex (14)"

        Returns:
            str: Function name or empty string
        """
        if "'" in text:
            # Format: "'function_name' is too complex (14)"
            parts = text.split("'")
            if len(parts) >= 2:
                return parts[1]
        return ""


# Register linter
if HAS_MCCABE:
    McCabeLinter()
else:
    LOGGER.warning("mccabe is not available. Install with: pip install mccabe")