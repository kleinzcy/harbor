"""
Core transformation logic for parameterized tests.
"""

from typing import Any, Optional, Sequence, Callable, Union
from .param import param
from .validation import (
    normalize_argnames,
    validate_argvalues,
    validate_ids,
    extract_parameter_set,
    is_async_function,
)
from .utils import generate_method_name, format_parameters, add_error_note, extract_param_id


class ParameterizedMethod:
    """Represents a parameterized test method.

    Stores decorator configuration and can generate concrete test methods.
    """

    def __init__(
        self,
        func: Callable,
        argnames: Union[str, Sequence[str]],
        argvalues: Sequence[Any],
        ids: Optional[Union[Sequence[Optional[str]], Callable]] = None,
    ):
        """Initialize parameterized method.

        Args:
            func: Original test method function.
            argnames: Argument names (string or sequence).
            argvalues: Sequence of parameter values.
            ids: Optional custom IDs or callable.

        Raises:
            Various validation errors.
        """
        self.func = func
        self.base_name = func.__name__
        self.is_async = is_async_function(func)

        # Normalize and validate
        self.argnames = normalize_argnames(argnames)
        validate_argvalues(argvalues, self.argnames)

        # Extract IDs from param objects first
        param_ids = [extract_param_id(v) for v in argvalues]

        # Validate and normalize ids parameter
        validated_ids = validate_ids(ids, argvalues)

        # Combine IDs: param.id takes precedence over ids parameter
        self.ids = [
            param_id if param_id is not None else validated_id
            for param_id, validated_id in zip(param_ids, validated_ids)
        ]

        self.argvalues = argvalues
        self.num_cases = len(argvalues)

        # Store parameter dicts for error enhancement
        self.parameter_dicts = [
            extract_parameter_set(value, self.argnames)
            for value in argvalues
        ]

    def generate_test_method(self, index: int) -> Callable:
        """Generate a concrete test method for parameter set at index.

        Args:
            index: Parameter set index (0-based).

        Returns:
            Test method function (sync or async).
        """
        if index < 0 or index >= self.num_cases:
            raise IndexError(f"Parameter set index {index} out of range")

        value = self.argvalues[index]
        param_dict = self.parameter_dicts[index]
        custom_id = self.ids[index]

        # Capture variables for closure
        func = self.func
        argnames = self.argnames
        base_name = self.base_name

        # Create the method
        if self.is_async:

            async def test_method(self):
                # Extract parameters
                if isinstance(value, param):
                    args = value.args
                elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                    args = tuple(value)
                else:
                    args = (value,)

                try:
                    return await func(self, *args)
                except Exception as exc:
                    # Enhance error with parameter info
                    note = f"Test parameters: {format_parameters(argnames, param_dict)}"
                    add_error_note(exc, note)
                    raise

        else:

            def test_method(self):
                # Extract parameters
                if isinstance(value, param):
                    args = value.args
                elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                    args = tuple(value)
                else:
                    args = (value,)

                try:
                    return func(self, *args)
                except Exception as exc:
                    # Enhance error with parameter info
                    note = f"Test parameters: {format_parameters(argnames, param_dict)}"
                    add_error_note(exc, note)
                    raise

        # Set method metadata
        test_method.__name__ = generate_method_name(
            base_name, index, custom_id
        )
        test_method.__doc__ = func.__doc__
        test_method.__module__ = func.__module__

        # Copy other attributes
        for attr in ("__dict__", "__annotations__"):
            if hasattr(func, attr):
                setattr(test_method, attr, getattr(func, attr))

        # Mark as generated
        test_method._is_parametrized_generated = True
        test_method._parametrized_original = func
        test_method._parametrized_index = index

        return test_method

    def apply_to_class(self, cls: type) -> None:
        """Apply parameterization to class by generating test methods.

        Args:
            cls: Test case class to modify.

        Raises:
            ValueError: If generated method name conflicts with existing attribute.
        """
        # Remove original method from class
        if self.base_name in cls.__dict__:
            delattr(cls, self.base_name)

        # Generate and add test methods
        for i in range(self.num_cases):
            method = self.generate_test_method(i)
            method_name = method.__name__

            # Check for name conflict
            if hasattr(cls, method_name):
                raise ValueError(
                    f"Duplicate test name '{method_name}' in class {cls.__name__}"
                )

            setattr(cls, method_name, method)