#!/usr/bin/env python3
"""Debug script to check what attributes unittest.mock.patch adds to functions."""

import unittest.mock
import inspect

def original_func():
    pass

# Apply patch decorator
patched_func = unittest.mock.patch('builtins.print')(original_func)

print(f"Function name: {patched_func.__name__}")
print(f"Has __wrapped__: {hasattr(patched_func, '__wrapped__')}")
print(f"Has patchings: {hasattr(patched_func, 'patchings')}")
print(f"Has __functools_wrapped__: {hasattr(patched_func, '__functools_wrapped__')}")

# List all attributes
print("\nAll attributes:")
for attr_name in dir(patched_func):
    if not attr_name.startswith('_'):
        continue
    try:
        attr_value = getattr(patched_func, attr_name)
        print(f"  {attr_name}: {type(attr_value).__name__}")
    except:
        print(f"  {attr_name}: <unable to get>")

# Check code object
try:
    print(f"\n__code__.co_name: {patched_func.__code__.co_name}")
    print(f"__name__: {patched_func.__name__}")
    print(f"Match: {patched_func.__code__.co_name == patched_func.__name__}")
except AttributeError as e:
    print(f"\nError accessing code object: {e}")

# Let's also check if it's a function or something else
print(f"\nType: {type(patched_func)}")
print(f"Is function: {inspect.isfunction(patched_func)}")
print(f"Is method: {inspect.ismethod(patched_func)}")
print(f"Callable: {callable(patched_func)}")