# -*- coding: utf-8 -*-
"""Isort integration for Pylama."""

import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    import isort
    from isort.exceptions import FileSkipped
    HAS_ISORT = True
except ImportError:
    HAS_ISORT = False

from pylama.context import RunContext
from pylama.errors import Error as PylamaError
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class IsortLinter(LinterV2):
    """Isort linter for Pylama."""

    name = "isort"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add isort-specific arguments."""
        if not HAS_ISORT:
            return

        group = parser.add_argument_group("isort options")
        group.add_argument(
            "--isort-profile",
            default="",
            help="isort profile (black, django, pycharm, google, open_stack, plone, attrs, hug)",
        )
        group.add_argument(
            "--isort-line-length",
            type=int,
            default=79,
            help="Maximum line length",
        )
        group.add_argument(
            "--isort-multi-line",
            type=int,
            default=3,
            choices=[0, 3, 4, 5, 6],
            help="Multi-line output (0: grid, 3: vertical, 4: hanging, 5: vertical-hanging, 6: vertical-grid)",
        )
        group.add_argument(
            "--isort-known-first-party",
            default="",
            help="Comma-separated list of modules to treat as first party",
        )
        group.add_argument(
            "--isort-known-third-party",
            default="",
            help="Comma-separated list of modules to treat as third party",
        )
        group.add_argument(
            "--isort-known-local-folder",
            default="",
            help="Comma-separated list of modules to treat as local folder",
        )
        group.add_argument(
            "--isort-lines-after-imports",
            type=int,
            default=-1,
            help="Empty lines after imports",
        )
        group.add_argument(
            "--isort-lines-between-types",
            type=int,
            default=0,
            help="Empty lines between import types",
        )
        group.add_argument(
            "--isort-force-sort-within-sections",
            action="store_true",
            help="Force sorting within sections",
        )
        group.add_argument(
            "--isort-order-by-type",
            action="store_true",
            help="Order imports by type",
        )
        group.add_argument(
            "--isort-force-alphabetical-sort-within-sections",
            action="store_true",
            help="Force alphabetical sorting within sections",
        )
        group.add_argument(
            "--isort-force-single-line",
            action="store_true",
            help="Force all imports to be single line",
        )
        group.add_argument(
            "--isort-skip",
            default="",
            help="Files to skip (comma-separated)",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[PylamaError]:
        """Run isort check."""
        if not HAS_ISORT:
            LOGGER.warning("isort is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Check if file should be skipped
        skip_list = params.get("isort_skip", "").split(",")
        if str(ctx.filepath) in skip_list:
            return []

        # Create isort config
        config = self._create_config(params)

        try:
            # Check if imports are sorted correctly
            check_result = isort.check_code(ctx.content, **config)

            if check_result:
                # Imports are already correctly sorted
                return []
            else:
                # Imports need sorting
                # Get the diff to provide helpful message
                sorted_code = isort.code(ctx.content, **config)

                # Create a warning about unsorted imports
                error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=1,
                    col=1,
                    text="Imports are incorrectly sorted",
                    number="I001",
                    type="W",  # Warning
                    source=self.name,
                )
                return [error]

        except FileSkipped:
            # File was skipped (e.g., no imports)
            return []
        except Exception as e:
            LOGGER.warning("Isort failed on %s: %s", ctx.filepath, e)
            return []

    def _create_config(self, params: dict) -> dict:
        """Create isort configuration from parameters."""
        config = {}

        # Set profile
        profile = params.get("isort_profile", "")
        if profile:
            config["profile"] = profile

        # Set line length
        line_length = params.get("isort_line_length", 79)
        config["line_length"] = line_length

        # Set multi-line output
        multi_line = params.get("isort_multi_line", 3)
        config["multi_line_output"] = multi_line

        # Set known modules
        known_first_party = params.get("isort_known_first_party", "")
        if known_first_party:
            config["known_first_party"] = [
                m.strip() for m in known_first_party.split(",") if m.strip()
            ]

        known_third_party = params.get("isort_known_third_party", "")
        if known_third_party:
            config["known_third_party"] = [
                m.strip() for m in known_third_party.split(",") if m.strip()
            ]

        known_local_folder = params.get("isort_known_local_folder", "")
        if known_local_folder:
            config["known_local_folder"] = [
                m.strip() for m in known_local_folder.split(",") if m.strip()
            ]

        # Set lines after imports
        lines_after_imports = params.get("isort_lines_after_imports", -1)
        if lines_after_imports >= 0:
            config["lines_after_imports"] = lines_after_imports

        # Set lines between types
        lines_between_types = params.get("isort_lines_between_types", 0)
        config["lines_between_types"] = lines_between_types

        # Set boolean flags
        if params.get("isort_force_sort_within_sections"):
            config["force_sort_within_sections"] = True

        if params.get("isort_order_by_type"):
            config["order_by_type"] = True

        if params.get("isort_force_alphabetical_sort_within_sections"):
            config["force_alphabetical_sort_within_sections"] = True

        if params.get("isort_force_single_line"):
            config["force_single_line"] = True

        # Set check-only mode
        config["check_only"] = True

        return config


# Register linter
if HAS_ISORT:
    IsortLinter()
else:
    LOGGER.warning("isort is not available. Install with: pip install isort")