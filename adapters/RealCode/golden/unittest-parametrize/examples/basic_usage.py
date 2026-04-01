#!/usr/bin/env python3
"""Basic usage example for unittest-parametrize."""

import sys
sys.path.insert(0, "src")

from unittest_parametrize import parametrize, ParametrizedTestCase, param
import unittest


class TestSquare(ParametrizedTestCase):
    @parametrize("x,expected", [(1, 1), (2, 4), (3, 9)])
    def test_square(self, x, expected):
        self.assertEqual(x * x, expected)


class TestCustomIDs(ParametrizedTestCase):
    @parametrize("value,expected", [
        param("hello", 5, id="string"),
        param([1, 2, 3], 3, id="list"),
        param({}, 0, id="empty"),
    ])
    def test_length(self, value, expected):
        self.assertEqual(len(value), expected)


if __name__ == "__main__":
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSquare)
    suite.addTests(loader.loadTestsFromTestCase(TestCustomIDs))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)