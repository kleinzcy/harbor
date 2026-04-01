"""
pysonDB-v2 - A lightweight JSON database library for Python.

Provides simple CRUD operations on local JSON files with schema management,
advanced querying, and a command-line interface.
"""

__version__ = "2.0.0"
__author__ = "pysonDB-v2 Developers"

from .db import PysonDB
from .errors import (
    IdDoesNotExistError,
    UnknownKeyError,
    SchemaTypeError,
)

__all__ = [
    "PysonDB",
    "IdDoesNotExistError",
    "UnknownKeyError",
    "SchemaTypeError",
]