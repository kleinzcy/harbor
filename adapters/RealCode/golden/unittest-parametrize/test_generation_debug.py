#!/usr/bin/env python3
"""Debug generation test failure."""

import sys
sys.path.insert(0, 'src')

from unittest_parametrize import parametrize
import io

print("Testing generation case...")

# Simulate what run_generation_case does
base_name = "test_square"

def test_func(self):
    pass

test_func.__name__ = base_name

print("\nCreated test_func:")
print(f"  __name__: {test_func.__name__}")
print(f"  Has __wrapped__: {hasattr(test_func, '__wrapped__')}")
print(f"  Has patchings: {hasattr(test_func, 'patchings')}")
print(f"  Has __functools_wrapped__: {hasattr(test_func, '__functools_wrapped__')}")
try:
    print(f"  __code__.co_name: {test_func.__code__.co_name}")
    print(f"  Match: {test_func.__code__.co_name == test_func.__name__}")
except:
    print("  __code__.co_name: N/A")

# Redirect stderr to capture debug output
stderr_capture = io.StringIO()
old_stderr = sys.stderr
sys.stderr = stderr_capture

try:
    print("\nApplying @parametrize decorator...")
    decorated = parametrize("x,expected", [(1, 1), (2, 4)])(test_func)
    print("Success!")
except RuntimeError as e:
    print(f"RuntimeError: {e}")
except Exception as e:
    print(f"Other error: {type(e).__name__}: {e}")
finally:
    sys.stderr = old_stderr

print("\n=== Debug output from _has_other_decorators ===")
print(stderr_capture.getvalue())