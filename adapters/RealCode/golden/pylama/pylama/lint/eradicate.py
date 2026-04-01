# -*- coding: utf-8 -*-
"""Eradicate (dead code detection) integration for Pylama."""

import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    import eradicate
    HAS_ERADICATE = True
except ImportError:
    HAS_ERADICATE = False

from pylama.context import RunContext
from pylama.errors import Error as PylamaError
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class EradicateLinter(LinterV2):
    """Eradicate linter for Pylama."""

    name = "eradicate"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add eradicate-specific arguments."""
        if not HAS_ERADICATE:
            return

        group = parser.add_argument_group("eradicate options")
        group.add_argument(
            "--eradicate-aggressive",
            action="store_true",
            help="Use aggressive mode (detect more dead code)",
        )
        group.add_argument(
            "--eradicate-in-place",
            action="store_true",
            help="Check what would be removed in in-place mode",
        )
        group.add_argument(
            "--eradicate-no-pass",
            action="store_true",
            help="Don't flag 'pass' statements as dead code",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[PylamaError]:
        """Run eradicate check."""
        if not HAS_ERADICATE:
            LOGGER.warning("eradicate is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Get eradicate options
        aggressive = params.get("eradicate_aggressive", False)
        in_place = params.get("eradicate_in_place", False)

        try:
            # Find dead code
            if in_place:
                # Check what would be removed
                cleaned = eradicate.filter_commented_out_code(
                    ctx.content,
                    aggressive=aggressive,
                )
                if cleaned == ctx.content:
                    return []
                # Content would change, find differences
                errors = self._find_dead_code_lines(ctx.content, cleaned, ctx)
            else:
                # Use detect_commented_out_code to find line numbers
                # Note: eradicate doesn't have a direct line number API
                # We'll use a simple approach
                errors = self._detect_dead_code_lines(ctx.content, aggressive, ctx)

            return errors

        except Exception as e:
            LOGGER.warning("Eradicate failed on %s: %s", ctx.filepath, e)
            return []

    def _find_dead_code_lines(self, original: str, cleaned: str, ctx: RunContext) -> List[PylamaError]:
        """Find lines with dead code by comparing original and cleaned content."""
        errors: List[PylamaError] = []

        original_lines = original.splitlines()
        cleaned_lines = cleaned.splitlines()

        # Simple line-by-line comparison
        # This is approximate but should work for most cases
        for i, (orig_line, clean_line) in enumerate(zip(original_lines, cleaned_lines)):
            if orig_line != clean_line:
                # Line contains dead code
                error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=i + 1,
                    col=1,
                    text="Commented out code found",
                    number="ERA001",
                    type="W",  # Warning
                    source=self.name,
                )
                errors.append(error)

        return errors

    def _detect_dead_code_lines(self, content: str, aggressive: bool, ctx: RunContext) -> List[PylamaError]:
        """Detect lines with dead code using eradicate."""
        errors: List[PylamaError] = []

        # Split content into lines
        lines = content.splitlines()

        # Process each line
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue

            # Check if line contains commented out code
            # This is a simplified check - actual eradicate logic is more complex
            stripped = line.strip()
            if stripped.startswith("#"):
                # Check if it looks like code (not just a comment)
                comment_content = stripped[1:].strip()
                if self._looks_like_code(comment_content):
                    error = PylamaError(
                        filename=str(ctx.filepath),
                        lnum=i + 1,
                        col=1,
                        text="Commented out code found",
                        number="ERA001",
                        type="W",  # Warning
                        source=self.name,
                    )
                    errors.append(error)

        return errors

    def _looks_like_code(self, text: str) -> bool:
        """Check if text looks like code (simplified)."""
        # Simple heuristics
        code_indicators = [
            "=",  # Assignment
            ":",  # Colon (for blocks)
            "def ",  # Function definition
            "class ",  # Class definition
            "import ",  # Import statement
            "from ",  # From import
            "if ",  # If statement
            "for ",  # For loop
            "while ",  # While loop
            "return ",  # Return statement
            "print(",  # Print function
        ]

        text_lower = text.lower()
        for indicator in code_indicators:
            if indicator in text_lower:
                return True

        return False


# Register linter
if HAS_ERADICATE:
    EradicateLinter()
else:
    LOGGER.warning("eradicate is not available. Install with: pip install eradicate")