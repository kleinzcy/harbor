# -*- coding: utf-8 -*-
"""Checking context for linters."""

import re
from argparse import Namespace
from pathlib import Path
from typing import Dict, List, Any

from pylama.errors import Error

# Regex patterns
MODELINE_RE = re.compile(
    r"^\s*#\s+(?:pylama:)\s*((?:[\w_]*=[^:\n\s]+:?)+)", re.I | re.M
).search

SKIP_PATTERN = re.compile(r"# *noqa\b", re.I).search


class RunContext:
    """Context for code checking."""

    def __init__(
        self,
        filepath: Path,
        content: str,
        options: Namespace,
    ):
        """Initialize checking context.

        :param filepath: Path to the file being checked
        :param content: File content as string
        :param options: Configuration options
        """
        self.filepath = filepath
        self.content = content
        self.options = options
        self._errors: List[Error] = []

        # Parse modeline if present
        self.modeline_params: Dict[str, str] = {}
        self._parse_modeline()

    def _parse_modeline(self) -> None:
        """Parse modeline from file content."""
        match = MODELINE_RE(self.content)
        if match:
            params_str = match.group(1)
            for param in params_str.split(":"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    self.modeline_params[key.strip()] = value.strip()

    def get_params(self, linter_name: str) -> Dict[str, Any]:
        """Get the configuration parameters for a specific Linter.

        Parameters are merged from:
        1. Modeline (highest priority)
        2. Linter-specific configuration
        3. Global configuration

        :param linter_name: Name of the linter
        :return: Dictionary of parameters
        """
        params: Dict[str, Any] = {}

        # Get global options
        global_params = vars(self.options)

        # Get linter-specific options
        linter_params = {}
        linter_config_name = f"{linter_name}_params"
        if hasattr(self.options, linter_config_name):
            linter_params = getattr(self.options, linter_config_name, {})

        # Merge: modeline > linter-specific > global
        for key, value in global_params.items():
            if not key.startswith("_"):
                params[key] = value

        for key, value in linter_params.items():
            params[key] = value

        for key, value in self.modeline_params.items():
            params[key] = value

        return params

    def push(
        self,
        lnum: int = 1,
        col: int = 0,
        text: str = "",
        number: str = "",
        type: str = "E",
        source: str = "",
    ) -> None:
        """Add an error to the context.

        :param lnum: Line number
        :param col: Column number
        :param text: Error message
        :param number: Error code
        :param type: Error type (E, W, etc.)
        :param source: Error source (linter name)
        """
        error = Error(
            filename=str(self.filepath),
            lnum=lnum,
            col=col,
            text=text,
            number=number,
            type=type,
            source=source,
        )
        self._errors.append(error)

    @property
    def errors(self) -> List[Error]:
        """Get list of errors found in this context."""
        return self._errors

    def has_skip(self, line: str) -> bool:
        """Check if line has skip comment (noqa)."""
        return bool(SKIP_PATTERN(line))

    def should_skip(self, lnum: int, col: int = 0) -> bool:
        """Determine if error at given location should be skipped.

        Checks for noqa comments on the line.
        """
        lines = self.content.splitlines()
        if lnum <= 0 or lnum > len(lines):
            return False

        line = lines[lnum - 1]
        return self.has_skip(line)

    def update_params(self, **kwargs: Any) -> None:
        """Update context parameters."""
        for key, value in kwargs.items():
            setattr(self.options, key, value)