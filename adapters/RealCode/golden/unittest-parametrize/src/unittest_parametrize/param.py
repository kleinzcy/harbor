"""
param object for advanced parameter configuration.

Provides an immutable parameter container with optional custom ID.
"""

import re
from typing import Any, Tuple, Optional


class param:
    """Immutable parameter container with optional custom test ID.

    Attributes:
        args: Tuple of parameter values.
        id: Optional custom identifier for the parameter set.

    Raises:
        ValueError: If id is not a valid Python identifier suffix.
    """

    __slots__ = ("_args", "_id")

    # Regex for valid Python identifier suffix (alphanumeric plus underscores, not starting with number)
    _ID_REGEX = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    def __init__(self, *args: Any, id: Optional[str] = None) -> None:
        """Initialize param object.

        Args:
            *args: Parameter values.
            id: Custom identifier for this parameter set. Must be a valid
                Python identifier suffix (alphanumeric plus underscores,
                not starting with a number).

        Raises:
            ValueError: If id is not a valid Python identifier suffix.
        """
        self._args = args
        self._id = id

        if id is not None:
            if not self._ID_REGEX.match(id):
                raise ValueError(
                    f"Invalid param id '{id}': must be a valid Python identifier "
                    f"(alphanumeric plus underscores, not starting with a number)"
                )

    @property
    def args(self) -> Tuple[Any, ...]:
        """Tuple of parameter values."""
        return self._args

    @property
    def id(self) -> Optional[str]:
        """Custom identifier for this parameter set, if provided."""
        return self._id

    def __repr__(self) -> str:
        """Return string representation."""
        if self._id is None:
            return f"param{self._args}"
        else:
            return f"param{self._args}, id={self._id!r}"

    def __eq__(self, other: Any) -> bool:
        """Compare two param objects for equality."""
        if not isinstance(other, param):
            return NotImplemented
        return self._args == other._args and self._id == other._id

    def __hash__(self) -> int:
        """Compute hash based on args and id."""
        return hash((self._args, self._id))

    @classmethod
    def from_dict(cls, data: dict) -> "param":
        """Create param object from dictionary representation.

        Expected format: {"__type__": "param", "args": [...], "id": ...}

        Args:
            data: Dictionary with param data.

        Returns:
            param instance.

        Raises:
            ValueError: If data doesn't have "__type__": "param" or missing "args".
        """
        if data.get("__type__") != "param":
            raise ValueError(f"Expected __type__='param', got {data.get('__type__')!r}")

        args = data.get("args")
        if args is None:
            raise ValueError("Missing 'args' in param dict")

        param_id = data.get("id")
        return cls(*args, id=param_id)

    def to_dict(self) -> dict:
        """Convert param object to dictionary representation.

        Returns:
            Dictionary with "__type__": "param", "args", and optional "id".
        """
        result = {"__type__": "param", "args": list(self._args)}
        if self._id is not None:
            result["id"] = self._id
        return result