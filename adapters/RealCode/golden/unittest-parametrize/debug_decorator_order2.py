#!/usr/bin/env python3
"""Debug decorator application order more carefully."""

import sys
sys.path.insert(0, 'src')

from unittest_parametrize import parametrize, ParametrizedTestCase
import unittest.mock

print("Testing decorator application step by step...")

# Let's manually simulate what happens with:
# @unittest.mock.patch('builtins.print')
# @parametrize("x", [1, 2])
# def test_method(self, mock_print):
#     pass

print("\n=== Step 1: Define original function ===")
def test_method(self, mock_print):
    pass
print(f"Original function: {test_method}")
print(f"Original function name: {test_method.__name__}")

print("\n=== Step 2: Apply @parametrize decorator ===")
# This is what happens first (decorator closest to function)
parametrize_decorator = parametrize("x", [1, 2])
print(f"parametrize decorator instance: {parametrize_decorator}")
parametrized_func = parametrize_decorator(test_method)
print(f"After parametrize: {parametrized_func}")
print(f"  __name__: {parametrized_func.__name__}")
print(f"  Has __wrapped__: {hasattr(parametrized_func, '__wrapped__')}")
print(f"  Has patchings: {hasattr(parametrized_func, 'patchings')}")
print(f"  Has _is_parametrized: {hasattr(parametrized_func, '_is_parametrized')}")

print("\n=== Step 3: Apply @mock.patch decorator ===")
# This happens next (decorator further from function)
patch_decorator = unittest.mock.patch('builtins.print')
print(f"patch decorator: {patch_decorator}")
patched_func = patch_decorator(parametrized_func)
print(f"After patch: {patched_func}")
print(f"  __name__: {parametrized_func.__name__}")
print(f"  Has __wrapped__: {hasattr(patched_func, '__wrapped__')}")
print(f"  Has patchings: {hasattr(patched_func, 'patchings')}")
print(f"  Has _is_parametrized: {hasattr(patched_func, '_is_parametrized')}")

print("\n=== Step 4: Check what _has_other_decorators sees ===")
print("When parametrize.__call__ is invoked on test_method:")
print(f"  test_method has __wrapped__: {hasattr(test_method, '__wrapped__')}")
print(f"  test_method has patchings: {hasattr(test_method, 'patchings')}")
print("  test_method.__code__.co_name == test_method.__name__: ", end="")
try:
    print(test_method.__code__.co_name == test_method.__name__)
except:
    print("N/A")

print("\n=== Step 5: Let's check the actual decorator syntax ===")
print("Creating class with decorators...")

# First, enable debug output in parametrize._has_other_decorators
import unittest_parametrize.decorators
original_method = unittest_parametrize.decorators.parametrize._has_other_decorators

def debug_method(func):
    import sys
    sys.stderr.write(f"\n[DEBUG] _has_other_decorators called on {func.__name__}\n")
    sys.stderr.write(f"[DEBUG]   __wrapped__: {hasattr(func, '__wrapped__')}\n")
    sys.stderr.write(f"[DEBUG]   patchings: {hasattr(func, 'patchings')}\n")
    sys.stderr.write(f"[DEBUG]   __functools_wrapped__: {hasattr(func, '__functools_wrapped__')}\n")
    try:
        sys.stderr.write(f"[DEBUG]   co_name: {func.__code__.co_name} vs __name__: {func.__name__}\n")
    except:
        sys.stderr.write("[DEBUG]   co_name: N/A\n")
    result = original_method(func)
    sys.stderr.write(f"[DEBUG]   Returns: {result}\n")
    return result

unittest_parametrize.decorators.parametrize._has_other_decorators = staticmethod(debug_method)

# Reload parametrize to use patched method
import importlib
importlib.reload(unittest_parametrize.decorators)
from unittest_parametrize.decorators import parametrize as parametrize_debug

print("\nTrying to create class with @patch then @parametrize:")
try:
    class TestClass(ParametrizedTestCase):
        @unittest.mock.patch('builtins.print')
        @parametrize_debug("x", [1, 2])
        def test_method(self, mock_print):
            pass
    print("No error raised!")
except RuntimeError as e:
    print(f"RuntimeError: {e}")
except Exception as e:
    print(f"Other error: {type(e).__name__}: {e}")