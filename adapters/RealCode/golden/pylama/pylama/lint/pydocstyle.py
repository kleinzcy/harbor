# -*- coding: utf-8 -*-
"""Pydocstyle (formerly pep257) integration for Pylama."""

import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

try:
    import pydocstyle
    from pydocstyle.violations import Error
    HAS_PYDOCSTYLE = True
except ImportError:
    HAS_PYDOCSTYLE = False

from pylama.context import RunContext
from pylama.errors import Error as PylamaError
from pylama.lint import LinterV2

LOGGER = logging.getLogger("pylama")


class PydocstyleLinter(LinterV2):
    """Pydocstyle linter for Pylama."""

    name = "pydocstyle"
    abstract = False

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add pydocstyle-specific arguments."""
        if not HAS_PYDOCSTYLE:
            return

        group = parser.add_argument_group("pydocstyle options")
        group.add_argument(
            "--pydocstyle-convention",
            default="pep257",
            help="Select base set of checked errors by convention (pep257, numpy, google)",
        )
        group.add_argument(
            "--pydocstyle-ignore",
            default="",
            help="Comma-separated list of error codes to ignore",
        )
        group.add_argument(
            "--pydocstyle-select",
            default="",
            help="Comma-separated list of error codes to select",
        )
        group.add_argument(
            "--pydocstyle-add-ignore",
            default="",
            help="Comma-separated list of error codes to add to ignore list",
        )
        group.add_argument(
            "--pydocstyle-add-select",
            default="",
            help="Comma-separated list of error codes to add to select list",
        )
        group.add_argument(
            "--pydocstyle-match",
            default="(?!test_).*\\.py",
            help="Check only files that exactly match this regular expression",
        )
        group.add_argument(
            "--pydocstyle-match-dir",
            default="[^\\.].*",
            help="Search only dirs that exactly match this regular expression",
        )

    def allow(self, path: Path) -> bool:
        """Check if file is a Python file."""
        return path.suffix == ".py"

    def run_check(self, ctx: RunContext) -> List[PylamaError]:
        """Run pydocstyle check."""
        if not HAS_PYDOCSTYLE:
            LOGGER.warning("pydocstyle is not installed")
            return []

        # Get parameters from context
        params = ctx.get_params(self.name)

        # Create temporary file with content
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(ctx.content)
            temp_path = f.name

        try:
            # Check the code using pydocstyle
            # pydocstyle.check() expects list of file paths
            errors = []
            for error in pydocstyle.check([temp_path]):
                # Skip if error should be ignored due to noqa comment
                if ctx.should_skip(error.line, 0):
                    continue

                pylama_error = PylamaError(
                    filename=str(ctx.filepath),
                    lnum=error.line,
                    col=1,  # pydocstyle doesn't provide column
                    text=f"{error.code}: {error.message}",
                    number=error.code,
                    type="W",  # Docstring issues are warnings
                    source=self.name,
                )
                errors.append(pylama_error)

            return errors

        except Exception as e:
            LOGGER.warning("Pydocstyle failed on %s: %s", ctx.filepath, e)
            return []
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _create_config(self, params: dict):
        """Create pydocstyle configuration from parameters."""
        config = pydocstyle.config.ConfigurationParser()

        # Set convention
        convention = params.get("pydocstyle_convention", "pep257")
        config.convention = convention

        # Set ignore patterns
        if "pydocstyle_ignore" in params and params["pydocstyle_ignore"]:
            config.ignore = set(params["pydocstyle_ignore"].split(","))

        # Set select patterns
        if "pydocstyle_select" in params and params["pydocstyle_select"]:
            config.select = set(params["pydocstyle_select"].split(","))

        # Add ignore patterns
        if "pydocstyle_add_ignore" in params and params["pydocstyle_add_ignore"]:
            config.add_ignore = set(params["pydocstyle_add_ignore"].split(","))

        # Add select patterns
        if "pydocstyle_add_select" in params and params["pydocstyle_add_select"]:
            config.add_select = set(params["pydocstyle_add_select"].split(","))

        # Set match patterns
        if "pydocstyle_match" in params:
            config.match = params["pydocstyle_match"]

        if "pydocstyle_match_dir" in params:
            config.match_dir = params["pydocstyle_match_dir"]

        return config


# Register linter
if HAS_PYDOCSTYLE:
    PydocstyleLinter()
else:
    LOGGER.warning("pydocstyle is not available. Install with: pip install pydocstyle")