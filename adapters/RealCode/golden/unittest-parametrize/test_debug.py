#!/usr/bin/env python3
"""Test with debug output enabled."""

import sys
sys.path.insert(0, 'src')

from unittest_parametrize import parametrize, ParametrizedTestCase
import unittest.mock

print("Testing with debug output...")

# Redirect stderr to capture debug output
import io
stderr_capture = io.StringIO()
old_stderr = sys.stderr
sys.stderr = stderr_capture

try:
    class TestClass(ParametrizedTestCase):
        @unittest.mock.patch('builtins.print')
        @parametrize("x", [1, 2])
        def test_method(self, mock_print):
            pass

    print("No error raised!")
except RuntimeError as e:
    print(f"RuntimeError: {e}")
except Exception as e:
    print(f"Other error: {type(e).__name__}: {e}")
finally:
    sys.stderr = old_stderr

print("\n=== Debug output ===")
print(stderr_capture.getvalue())