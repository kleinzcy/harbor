"""
Input validation utilities for unittest-parametrize.
"""

import inspect
from typing import Any, List, Sequence, Union, Callable, Optional
from .param import param


def normalize_argnames(
    argnames: Union[str, Sequence[str]]
) -> List[str]:
    """Normalize argument names to list of strings.

    Args:
        argnames: Either a comma-separated string or sequence of strings.

    Returns:
        List of argument name strings with whitespace stripped.

    Raises:
        TypeError: If argnames is not a string or sequence of strings.
        ValueError: If any argument name is empty after stripping.
    """
    if isinstance(argnames, str):
        # Split by commas, strip whitespace
        parts = [part.strip() for part in argnames.split(",")]
        # Remove empty strings
        argnames_list = [part for part in parts if part]
    else:
        # Assume sequence, convert to list
        try:
            argnames_list = [str(name).strip() for name in argnames]
        except (TypeError, ValueError):
            raise TypeError(
                f"argnames must be string or sequence of strings, got {type(argnames).__name__}"
            )

    # Validate each name
    for i, name in enumerate(argnames_list):
        if not name:
            raise ValueError(f"Argument name at index {i} is empty after stripping")

    return argnames_list


def validate_argvalues(
    argvalues: Sequence[Any],
    argnames: List[str],
) -> None:
    """Validate argvalues against argnames.

    Args:
        argvalues: Sequence of parameter values (tuples or param objects).
        argnames: List of argument names.

    Raises:
        TypeError: If argvalues is not a sequence.
        ValueError: If any argvalue has wrong number of arguments.
    """
    if not isinstance(argvalues, Sequence):
        raise TypeError(f"argvalues must be a sequence, got {type(argvalues).__name__}")

    num_args = len(argnames)

    for i, value in enumerate(argvalues):
        if isinstance(value, param):
            actual_args = len(value.args)
        elif isinstance(value, Sequence):
            actual_args = len(value)
        else:
            # Single value for single argument case
            if num_args == 1:
                # Check if value is a dict (not allowed as single value)
                if isinstance(value, dict):
                    raise TypeError(
                        f"argvalue at index {i} is not a tuple or param instance"
                    )
                continue
            else:
                raise TypeError(
                    f"argvalue at index {i} is not a tuple or param instance"
                )

        # For param objects or sequences, check length matches
        if isinstance(value, (param, Sequence)) and actual_args != num_args:
            if isinstance(value, param):
                raise ValueError(
                    f"param object at index {i} has wrong number of arguments "
                    f"({actual_args} != {num_args})"
                )
            else:
                raise ValueError(
                    f"tuple at index {i} has wrong number of arguments "
                    f"({actual_args} != {num_args})"
                )


def validate_ids(
    ids: Optional[Union[Sequence[Optional[str]], Callable]],
    argvalues: Sequence[Any],
) -> List[Optional[str]]:
    """Validate and normalize ids parameter.

    Args:
        ids: Either None, sequence of strings/None, or callable.
        argvalues: Sequence of parameter values.

    Returns:
        List of ID strings or None values.

    Raises:
        TypeError: If ids has wrong type.
        ValueError: If ids length doesn't match argvalues, or duplicate IDs.
    """
    if ids is None:
        return [None] * len(argvalues)

    if callable(ids):
        # Apply callable to each parameter set
        id_list = []
        for i, value in enumerate(argvalues):
            if isinstance(value, param):
                # For param objects, use args
                id_parts = ids(*value.args)
            elif isinstance(value, Sequence):
                id_parts = ids(*value)
            else:
                # Single value
                id_parts = ids(value)

            if isinstance(id_parts, str):
                id_str = id_parts
            else:
                # Assume iterable of strings
                try:
                    id_str = "_".join(str(part) for part in id_parts)
                except TypeError:
                    raise TypeError(
                        f"ids callable returned non-string/iterable for index {i}: {id_parts}"
                    )

            id_list.append(id_str if id_str else None)
        return id_list

    # ids is a sequence
    if not isinstance(ids, Sequence):
        raise TypeError(
            f"ids must be None, callable, or sequence, got {type(ids).__name__}"
        )

    if len(ids) != len(argvalues):
        raise ValueError(
            f"ids length ({len(ids)}) doesn't match argvalues length ({len(argvalues)})"
        )

    # Convert to list, preserving None
    id_list = []
    for i, id_val in enumerate(ids):
        if id_val is None:
            id_list.append(None)
        else:
            id_str = str(id_val)
            id_list.append(id_str if id_str else None)

    # Check for duplicate non-None IDs
    seen = set()
    for i, id_val in enumerate(id_list):
        if id_val is not None:
            if id_val in seen:
                raise ValueError(f"Duplicate param id '{id_val}'")
            seen.add(id_val)

    return id_list


def extract_parameter_set(
    value: Any,
    argnames: List[str],
) -> dict:
    """Extract parameter dict from value (tuple, param, or single value).

    Args:
        value: Parameter value (tuple, param object, or single value).
        argnames: List of argument names.

    Returns:
        Dictionary mapping argname to value.
    """
    if isinstance(value, param):
        args = value.args
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        args = tuple(value)
    else:
        # Single value for single argument
        args = (value,)

    if len(args) != len(argnames):
        raise ValueError(
            f"Parameter set has wrong number of arguments ({len(args)} != {len(argnames)})"
        )

    return dict(zip(argnames, args))


def is_async_function(func: Callable) -> bool:
    """Check if function is a coroutine function.

    Args:
        func: Function to check.

    Returns:
        True if function is async def.
    """
    return inspect.iscoroutinefunction(func)