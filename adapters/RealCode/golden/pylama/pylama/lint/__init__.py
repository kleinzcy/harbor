# -*- coding: utf-8 -*-
"""Linter interface and registry."""

import abc
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Type, Optional, Any

from pylama.errors import Error

LOGGER = logging.getLogger("pylama")


class LinterMeta(abc.ABCMeta):
    """Metaclass that builds linter classes with parameters."""

    def __new__(mcs, name: str, bases: tuple, params: dict) -> type:
        """Create new linter class."""
        cls = super().__new__(mcs, name, bases, params)
        if name != "LinterV2" and not getattr(cls, "abstract", False):
            # Register linter
            LINTERS[cls.name] = cls
        return cls


class LinterV2(metaclass=LinterMeta):
    """Base class for all code checkers."""

    name: str = "unknown"
    abstract: bool = True  # Mark as abstract base class

    @classmethod
    def add_args(cls, parser: ArgumentParser) -> None:
        """Add command-line arguments specific to this Linter."""

    def allow(self, path: Path) -> bool:
        """Determine whether this Linter can check the specified file.

        Default implementation checks file extension.
        """
        return path.suffix == ".py"

    @abc.abstractmethod
    def run_check(self, ctx: "RunContext") -> List[Error]:
        """Perform code checks and return a list of errors."""
        raise NotImplementedError

    def __repr__(self) -> str:
        """Return representation of linter."""
        return f"{self.__class__.__name__}(name={self.name!r})"


# Registry of all available linters
LINTERS: Dict[str, Type[LinterV2]] = {}


def get_linter(name: str) -> Optional[Type[LinterV2]]:
    """Get linter class by name."""
    return LINTERS.get(name)


def register_linter(linter_class: Type[LinterV2]) -> Type[LinterV2]:
    """Register a linter class."""
    LINTERS[linter_class.name] = linter_class
    return linter_class


def available_linters() -> List[str]:
    """Get names of all registered linters."""
    return list(LINTERS.keys())