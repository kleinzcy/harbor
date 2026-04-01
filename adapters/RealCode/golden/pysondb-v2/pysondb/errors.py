"""
Custom exceptions for pysonDB-v2.
"""


class IdDoesNotExistError(Exception):
    """Raised when an operation references a non-existent ID."""
    pass


class UnknownKeyError(Exception):
    """Raised when data contains unknown fields or misses required fields."""
    pass


class SchemaTypeError(Exception):
    """Raised when database structure is invalid or corrupted."""
    pass