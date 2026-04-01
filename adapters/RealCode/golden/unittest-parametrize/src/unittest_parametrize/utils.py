"""
Utility functions for unittest-parametrize.
"""

import sys
from typing import Any, Optional, List, Dict


def generate_method_name(
    base_name: str,
    index: int,
    custom_id: Optional[str] = None,
) -> str:
    """Generate test method name.

    Args:
        base_name: Original test method name.
        index: Parameter set index (0-based).
        custom_id: Optional custom identifier.

    Returns:
        Generated method name with suffix.
    """
    if custom_id is not None:
        # Custom ID becomes the suffix
        suffix = custom_id
    else:
        # Default numeric suffix
        suffix = str(index)

    return f"{base_name}_{suffix}"


def format_parameters(
    argnames: List[str],
    parameters: Dict[str, Any],
) -> str:
    """Format parameters for error message.

    Args:
        argnames: List of argument names.
        parameters: Dictionary of parameter values.

    Returns:
        Formatted string like "x=1, expected=2".
    """
    parts = []
    for name in argnames:
        value = parameters[name]
        # Use repr for values, but keep simple formatting for basic types
        parts.append(f"{name}={value!r}")
    return ", ".join(parts)


def add_error_note(
    exception: BaseException,
    note: str,
) -> None:
    """Add note to exception if Python version >= 3.11.

    Args:
        exception: Exception to add note to.
        note: Note text to add.
    """
    if sys.version_info >= (3, 11):
        exception.add_note(note)


def extract_param_id(
    value: Any,
) -> Optional[str]:
    """Extract custom ID from parameter value.

    Args:
        value: Parameter value (tuple, param object, or single value).

    Returns:
        Custom ID if value is param object with id, else None.
    """
    from .param import param

    if isinstance(value, param):
        return value.id
    return None