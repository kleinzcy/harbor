"""
@parametrize decorator for parameterizing test methods.
"""

from typing import Any, Sequence, Optional, Union, Callable
from .core import ParameterizedMethod


class parametrize:
    """Decorator for parameterizing test methods.

    Usage:
        @parametrize("x,expected", [(1, 1), (2, 4)])
        def test_square(self, x, expected):
            self.assertEqual(x * x, expected)
    """

    def __init__(
        self,
        argnames: Union[str, Sequence[str]],
        argvalues: Sequence[Any],
        ids: Optional[Union[Sequence[Optional[str]], Callable]] = None,
    ):
        """Initialize decorator.

        Args:
            argnames: Argument names (comma-separated string or sequence).
            argvalues: Sequence of parameter values (tuples or param objects).
            ids: Optional custom IDs (sequence or callable).
        """
        self.argnames = argnames
        self.argvalues = argvalues
        self.ids = ids

    def __call__(self, func: Callable) -> Callable:
        """Apply decorator to function.

        Args:
            func: Test method to parameterize.

        Returns:
            Wrapped function with parameterization metadata.

        Raises:
            RuntimeError: If decorator is not applied to a method of
                ParametrizedTestCase subclass.
        """
        # Check if already decorated with parametrize
        if hasattr(func, "_parametrize_decorator"):
            raise RuntimeError("@parametrize cannot be stacked")

        # Check if function has other decorators (parametrize must be outermost)
        if self._has_other_decorators(func):
            raise RuntimeError("@parametrize must be the top-most decorator")

        # Create ParameterizedMethod instance and attach as metadata
        param_method = ParameterizedMethod(func, self.argnames, self.argvalues, self.ids)
        func._parametrize_decorator = param_method

        # Mark function as parameterized
        func._is_parametrized = True

        # Return function unchanged - actual transformation happens in
        # ParametrizedTestCase.__init_subclass__
        return func

    @staticmethod
    def _has_other_decorators(func: Callable) -> bool:
        """Check if function has been decorated by other decorators.

        Similar to testcase._has_other_decorators but doesn't depend on
        is_parametrized (since we haven't marked it yet).
        """
        import sys
        # Debug
        debug = False
        if debug:
            sys.stderr.write(f"Checking decorators on {func.__name__}: ")
            sys.stderr.write(f"__wrapped__={hasattr(func, '__wrapped__')} ")
            sys.stderr.write(f"patchings={hasattr(func, 'patchings')} ")
            sys.stderr.write(f"__functools_wrapped__={hasattr(func, '__functools_wrapped__')} ")
            try:
                sys.stderr.write(f"co_name={func.__code__.co_name} vs __name__={func.__name__}\n")
            except:
                pass

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


def is_parametrized(func: Callable) -> bool:
    """Check if function is decorated with @parametrize.

    Args:
        func: Function to check.

    Returns:
        True if function has @parametrize decorator.
    """
    return hasattr(func, "_is_parametrized")


def get_parametrized_method(func: Callable) -> ParameterizedMethod:
    """Get ParameterizedMethod instance from decorated function.

    Args:
        func: Parameterized function.

    Returns:
        ParameterizedMethod instance.

    Raises:
        ValueError: If function is not parameterized.
    """
    if not is_parametrized(func):
        raise ValueError(f"Function {func.__name__} is not parameterized")
    return func._parametrize_decorator