"""
ParametrizedTestCase base class for parameterized tests.
"""

import unittest
from .decorators import is_parametrized, get_parametrized_method


class ParametrizedTestCase(unittest.TestCase):
    """Base class for test cases with parameterized test methods.

    Automatically processes methods decorated with @parametrize and generates
    individual test methods for each parameter set.
    """

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Process parameterized methods when subclass is created.

        Args:
            **kwargs: Additional keyword arguments passed to class creation.

        Raises:
            RuntimeError: If @parametrize is not the outermost decorator.
            ValueError: For various validation errors.
        """
        super().__init_subclass__(**kwargs)

        # Process all methods in class
        for name, method in list(cls.__dict__.items()):
            if not callable(method):
                continue

            # Check if method is parameterized
            if is_parametrized(method):
                # Validate decorator ordering
                if _has_other_decorators(method):
                    raise RuntimeError("@parametrize must be the top-most decorator")

                # Get parameterized method configuration
                param_method = get_parametrized_method(method)

                # Apply parameterization
                param_method.apply_to_class(cls)


def _has_other_decorators(func) -> bool:
    """Check if function has been decorated by other decorators.

    Args:
        func: Function to check.

    Returns:
        True if function appears to have other decorators applied.
    """
    # Check for common decorator markers
    if hasattr(func, "__wrapped__"):
        return True

    # Check for unittest.mock.patch decorator markers
    if hasattr(func, "patchings"):
        return True

    # Check for functools.wraps markers
    if hasattr(func, "__functools_wrapped__"):
        return True

    # Check if function name doesn't match code object name
    # (some decorators rename the function)
    try:
        if func.__code__.co_name != func.__name__:
            return True
    except AttributeError:
        pass

    return False