#!/usr/bin/env python3
"""Simple test for error enhancement."""

import sys
sys.path.insert(0, 'src')

from unittest_parametrize import parametrize, ParametrizedTestCase
import unittest
import io

print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}")

# Create a failing test
class FailingTest(ParametrizedTestCase):
    @parametrize("x,expected", [(1, 2), (3, 8)])  # 1**2=1 != 2, 3**2=9 != 8
    def test_square(self, x, expected):
        self.assertEqual(x**2, expected)

# Run the test
suite = unittest.TestLoader().loadTestsFromTestCase(FailingTest)
output = io.StringIO()
runner = unittest.TextTestRunner(stream=output, verbosity=2)
result = runner.run(suite)

print("\n=== Test Output ===")
print(output.getvalue())

print("\n=== Failures ===")
if result.failures:
    for test, traceback in result.failures:
        print(f"Test: {test}")
        print(f"Traceback:\n{traceback}")
        print("-" * 80)

        # Check for error enhancement note
        if "Test parameters:" in traceback:
            print("✓ Error enhancement note found!")
        else:
            print("✗ Error enhancement note NOT found")
else:
    print("No failures (unexpected!)")