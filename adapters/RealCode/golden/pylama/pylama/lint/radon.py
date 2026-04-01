# -*- coding: utf-8 -*-
"""Radon (code metrics) integration for Pylama."""

import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    import radon
    from radon.complexity import cc_visit, cc_rank
    from radon.raw import analyze
    from radon.metrics import mi_visit
    from radon.maintenance import maintainability_index
    HAS_RADON = True
except ImportError:
    HAS_RADON = False

from pylama.context import RunContext
from pylama.errors import Error as PylamaError
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class RadonLinter(LinterV2):
    """Radon linter for Pylama."""

    name = "radon"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add radon-specific arguments."""
        if not HAS_RADON:
            return

        group = parser.add_argument_group("radon options")
        group.add_argument(
            "--radon-max-complexity",
            type=int,
            default=10,
            help="Maximum cyclomatic complexity allowed",
        )
        group.add_argument(
            "--radon-min-mi",
            type=int,
            default=30,
            help="Minimum maintainability index allowed",
        )
        group.add_argument(
            "--radon-max-loc",
            type=int,
            default=100,
            help="Maximum lines of code per function allowed",
        )
        group.add_argument(
            "--radon-max-lloc",
            type=int,
            default=50,
            help="Maximum logical lines of code per function allowed",
        )
        group.add_argument(
            "--radon-max-comments",
            type=float,
            default=0.3,
            help="Minimum comment ratio (comments/total lines)",
        )
        group.add_argument(
            "--radon-no-assert",
            action="store_true",
            help="Don't treat assert statements as complexity contributors",
        )
        group.add_argument(
            "--radon-multi",
            action="store_true",
            help="Enable multi-processing",
        )
        group.add_argument(
            "--radon-show-closures",
            action="store_true",
            help="Show closures in complexity analysis",
        )
        group.add_argument(
            "--radon-order",
            default="SCORE",
            choices=["SCORE", "LINES", "ALPHA"],
            help="Order of output (SCORE, LINES, ALPHA)",
        )
        group.add_argument(
            "--radon-include-ipynb",
            action="store_true",
            help="Include Jupyter notebooks",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[PylamaError]:
        """Run radon check."""
        if not HAS_RADON:
            LOGGER.warning("radon is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Get thresholds
        max_complexity = params.get("radon_max_complexity", 10)
        min_mi = params.get("radon_min_mi", 30)
        max_loc = params.get("radon_max_loc", 100)
        max_lloc = params.get("radon_max_lloc", 50)
        max_comments_ratio = params.get("radon_max_comments", 0.3)

        errors: List[PylamaError] = []

        try:
            # Check cyclomatic complexity
            cc_errors = self._check_complexity(ctx, max_complexity, params)
            errors.extend(cc_errors)

            # Check maintainability index
            mi_errors = self._check_maintainability(ctx, min_mi)
            errors.extend(mi_errors)

            # Check raw metrics (LOC, LLOC, comments)
            raw_errors = self._check_raw_metrics(ctx, max_loc, max_lloc, max_comments_ratio)
            errors.extend(raw_errors)

            return errors

        except Exception as e:
            LOGGER.warning("Radon failed on %s: %s", ctx.filepath, e)
            return []

    def _check_complexity(self, ctx: RunContext, max_complexity: int, params: dict) -> List[PylamaError]:
        """Check cyclomatic complexity."""
        errors: List[PylamaError] = []

        # Get options
        no_assert = params.get("radon_no_assert", False)
        show_closures = params.get("radon_show_closures", False)

        try:
            # Analyze complexity
            blocks = cc_visit(
                ctx.content,
                no_assert=no_assert,
                show_closures=show_closures,
            )

            for block in blocks:
                # Skip if error should be ignored due to noqa comment
                if ctx.should_skip(block.lineno, 0):
                    continue

                if block.complexity > max_complexity:
                    rank = cc_rank(block.complexity)
                    error = PylamaError(
                        filename=str(ctx.filepath),
                        lnum=block.lineno,
                        col=1,
                        text=f"Function '{block.name}' is too complex ({block.complexity}, rank {rank})",
                        number=f"CC{block.complexity:03d}",
                        type="W",  # Warning
                        source=self.name,
                    )
                    errors.append(error)

            return errors

        except SyntaxError:
            # Skip files with syntax errors
            return []

    def _check_maintainability_index(self, ctx: RunContext, min_mi: int) -> List[PylamaError]:
        """Check maintainability index."""
        errors: List[PylamaError] = []

        try:
            # Calculate maintainability index
            mi_result = maintainability_index(ctx.content)

            if mi_result < min_mi:
                # For file-level MI, use line 1
                error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=1,
                    col=1,
                    text=f"Maintainability index is too low ({mi_result:.1f})",
                    number=f"MI{int(mi_result):03d}",
                    type="W",  # Warning
                    source=self.name,
                )
                errors.append(error)

            return errors

        except Exception:
            return []

    def _check_raw_metrics(self, ctx: RunContext, max_loc: int, max_lloc: int, max_comments_ratio: float) -> List[PylamaError]:
        """Check raw metrics (LOC, LLOC, comments)."""
        errors: List[PylamaError] = []

        try:
            # Analyze raw metrics
            raw_metrics = analyze(ctx.content)

            # Check total lines
            if raw_metrics.loc > max_loc:
                error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=1,
                    col=1,
                    text=f"File has too many lines ({raw_metrics.loc} > {max_loc})",
                    number=f"LOC{raw_metrics.loc:03d}",
                    type="W",
                    source=self.name,
                )
                errors.append(error)

            # Check logical lines
            if raw_metrics.lloc > max_lloc:
                error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=1,
                    col=1,
                    text=f"File has too many logical lines ({raw_metrics.lloc} > {max_lloc})",
                    number=f"LLOC{raw_metrics.lloc:03d}",
                    type="W",
                    source=self.name,
                )
                errors.append(error)

            # Check comment ratio
            if raw_metrics.loc > 0:
                comment_ratio = raw_metrics.comments / raw_metrics.loc
                if comment_ratio < max_comments_ratio:
                    error = PylamaError(
                        filename=str(ctx.filepath),
                        lnum=1,
                        col=1,
                        text=f"File has low comment ratio ({comment_ratio:.1%} < {max_comments_ratio:.0%})",
                        number=f"COM{int(comment_ratio*100):03d}",
                        type="I",  # Info
                        source=self.name,
                    )
                    errors.append(error)

            return errors

        except Exception:
            return []


# Register linter
if HAS_RADON:
    RadonLinter()
else:
    LOGGER.warning("radon is not available. Install with: pip install radon")