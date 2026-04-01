#!/usr/bin/env python3
"""Debug decorator application order."""

import sys
sys.path.insert(0, 'src')

from unittest_parametrize import parametrize, ParametrizedTestCase
import unittest.mock

print("Testing decorator order...")

# This is how the test applies decorators:
# @unittest.mock.patch('builtins.print')
# @parametrize("x", [1, 2])
# def test_method(self, mock_print):
#     pass

# Let's see what happens step by step
def original_test_method(self, mock_print):
    pass

print("\n1. Applying @parametrize first:")
parametrized = parametrize("x", [1, 2])(original_test_method)
print(f"   Function name after parametrize: {parametrized.__name__}")
print(f"   Has __wrapped__: {hasattr(parametrized, '__wrapped__')}")
print(f"   Has patchings: {hasattr(parametrized, 'patchings')}")
print(f"   Has _is_parametrized: {hasattr(parametrized, '_is_parametrized')}")

print("\n2. Then applying @mock.patch:")
try:
    patched = unittest.mock.patch('builtins.print')(parametrized)
    print(f"   Function name after patch: {patched.__name__}")
    print(f"   Has __wrapped__: {hasattr(patched, '__wrapped__')}")
    print(f"   Has patchings: {hasattr(patched, 'patchings')}")
    print(f"   Has _is_parametrized: {hasattr(patched, '_is_parametrized')}")
except Exception as e:
    print(f"   Error applying patch: {e}")

print("\n3. Now let's try the opposite order (parametrize outermost):")
def original_test_method2(self, mock_print):
    pass

print("\n   First apply @mock.patch:")
patched2 = unittest.mock.patch('builtins.print')(original_test_method2)
print(f"   Function name after patch: {patched2.__name__}")
print(f"   Has __wrapped__: {hasattr(patched2, '__wrapped__')}")
print(f"   Has patchings: {hasattr(patched2, 'patchings')}")

print("\n   Then apply @parametrize:")
try:
    parametrized2 = parametrize("x", [1, 2])(patched2)
    print(f"   Function name after parametrize: {parametrized2.__name__}")
    print(f"   Has __wrapped__: {hasattr(parametrized2, '__wrapped__')}")
    print(f"   Has patchings: {hasattr(parametrized2, 'patchings')}")
    print(f"   Has _is_parametrized: {hasattr(parametrized2, '_is_parametrized')}")
except Exception as e:
    print(f"   Error applying parametrize: {e}")
    print(f"   Error type: {type(e).__name__}")

print("\n4. Let's test the actual class creation:")
print("\n   Case A: patch then parametrize (parametrize not outermost):")
try:
    class TestClassA(ParametrizedTestCase):
        @unittest.mock.patch('builtins.print')
        @parametrize("x", [1, 2])
        def test_method(self, mock_print):
            pass
    print("   No error raised!")
except RuntimeError as e:
    print(f"   RuntimeError: {e}")
except Exception as e:
    print(f"   Other error: {type(e).__name__}: {e}")

print("\n   Case B: parametrize then patch (parametrize outermost):")
try:
    class TestClassB(ParametrizedTestCase):
        @parametrize("x", [1, 2])
        @unittest.mock.patch('builtins.print')
        def test_method(self, mock_print):
            pass
    print("   No error raised!")
except RuntimeError as e:
    print(f"   RuntimeError: {e}")
except Exception as e:
    print(f"   Other error: {type(e).__name__}: {e}")