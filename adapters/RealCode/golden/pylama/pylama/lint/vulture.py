# -*- coding: utf-8 -*-
"""Vulture (unused code detection) integration for Pylama."""

import ast
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    import vulture
    HAS_VULTURE = True
except ImportError:
    HAS_VULTURE = False

from pylama.context import RunContext
from pylama.errors import Error as PylamaError
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class VultureLinter(LinterV2):
    """Vulture linter for Pylama."""

    name = "vulture"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add vulture-specific arguments."""
        if not HAS_VULTURE:
            return

        group = parser.add_argument_group("vulture options")
        group.add_argument(
            "--vulture-min-confidence",
            type=int,
            default=60,
            help="Minimum confidence (0-100) to report unused code",
        )
        group.add_argument(
            "--vulture-ignore-names",
            default="",
            help="Comma-separated list of names to ignore (e.g., '_,temp,unused')",
        )
        group.add_argument(
            "--vulture-ignore-decorators",
            default="",
            help="Comma-separated list of decorators to ignore",
        )
        group.add_argument(
            "--vulture-exclude",
            default="",
            help="Comma-separated list of patterns to exclude",
        )
        group.add_argument(
            "--vulture-sort-by-size",
            action="store_true",
            help="Sort unused code by size",
        )
        group.add_argument(
            "--vulture-make-whitelist",
            action="store_true",
            help="Generate whitelist from current unused code",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[PylamaError]:
        """Run vulture check."""
        if not HAS_VULTURE:
            LOGGER.warning("vulture is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Create vulture scanner with custom configuration
        min_confidence = params.get("vulture_min_confidence", 60)
        ignore_names = self._parse_comma_list(params.get("vulture_ignore_names", ""))
        ignore_decorators = self._parse_comma_list(params.get("vulture_ignore_decorators", ""))

        # Create scanner
        scanner = vulture.core.Scanner(
            min_confidence=min_confidence,
            ignore_names=ignore_names,
            ignore_decorators=ignore_decorators,
        )

        try:
            # Parse the code
            try:
                tree = ast.parse(ctx.content, str(ctx.filepath))
            except SyntaxError as e:
                # Handle syntax errors
                LOGGER.debug("Vulture syntax error in %s: %s", ctx.filepath, e)
                return []

            # Scan the AST
            scanner.scan(tree, str(ctx.filepath))

            # Get unused items
            errors: List[PylamaError] = []
            for item in scanner.get_unused_code():
                # Skip if error should be ignored due to noqa comment
                if ctx.should_skip(item.first_lineno, 0):
                    continue

                # Determine error type based on item type
                item_type = item.typ
                if item_type in ("function", "method", "class"):
                    error_type = "W"
                elif item_type in ("variable", "attribute", "property"):
                    error_type = "W"
                elif item_type in ("import", "importfrom"):
                    error_type = "W"
                else:
                    error_type = "W"

                # Create error message
                message = f"Unused {item_type} '{item.name}'"

                error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=item.first_lineno,
                    col=1,  # Vulture doesn't provide column numbers
                    text=message,
                    number=f"VUL{item.confidence:03d}",
                    type=error_type,
                    source=self.name,
                )
                errors.append(error)

            return errors

        except Exception as e:
            LOGGER.warning("Vulture failed on %s: %s", ctx.filepath, e)
            return []

    def _parse_comma_list(self, value: str) -> List[str]:
        """Parse comma-separated list."""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]


# Register linter
if HAS_VULTURE:
    VultureLinter()
else:
    LOGGER.warning("vulture is not available. Install with: pip install vulture")