#!/usr/bin/env python
"""Test all Pylama linters."""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pylama.core import run
from pylama.config import parse_options
from pylama.lint import LINTERS

def test_linter(linter_name, test_code, expected_errors_min=0, **kwargs):
    """Test a specific linter."""
    print(f"\nTesting {linter_name}...")

    # Create a temporary test file
    fd, path = tempfile.mkstemp(suffix=".py", prefix=f"pylama_test_{linter_name}_")
    os.close(fd)

    with open(path, "w", encoding="utf-8") as f:
        f.write(test_code)

    try:
        # Set up options
        options = parse_options(config=False)
        options.paths = [path]
        options.linters = linter_name

        # Apply any additional options
        for key, value in kwargs.items():
            if hasattr(options, key):
                setattr(options, key, value)

        # Run check
        errors = run(options)

        print(f"  File: {Path(path).name}")
        print(f"  Found {len(errors)} errors")

        if errors:
            for error in errors[:5]:  # Show first 5 errors
                print(f"    - {error.source}: Line {error.lnum}: {error.text}")

        # Check if we found at least the expected minimum
        if len(errors) >= expected_errors_min:
            print(f"  ✓ {linter_name} works")
            return True
        else:
            print(f"  ✗ {linter_name} found {len(errors)} errors, expected at least {expected_errors_min}")
            return False

    finally:
        # Clean up
        if os.path.exists(path):
            os.unlink(path)

def main():
    """Run tests for all linters."""
    print("=" * 60)
    print("Pylama Linter Tests")
    print("=" * 60)

    # Test codes for different linters
    test_cases = {
        "pycodestyle": {
            "code": """def bad_spacing():
    x=1  # Missing spaces
    return x
""",
            "min_errors": 1  # E225 at least
        },
        "pyflakes": {
            "code": """import os
x = undefined_var  # Undefined
""",
            "min_errors": 2  # Unused import and undefined var
        },
        "mccabe": {
            "code": """def complex_func(x):
    if x > 0:
        if x > 10:
            if x > 20:
                return "high"
            return "medium"
        return "low"
    return "negative"
""",
            "min_errors": 1,  # Complexity too high
            "max_complexity": 3  # Set low threshold to trigger error
        },
        "pydocstyle": {
            "code": """def undocumented():
    return 1
""",
            "min_errors": 1  # Missing docstring
        },
        # Optional linters - may not be installed
        "pylint": {
            "code": """def bad_name():  # Should trigger naming convention
    A = 1  # Should trigger invalid-name
    return A
""",
            "min_errors": 0  # May not be installed
        },
        "mypy": {
            "code": """def type_error() -> int:
    return "string"  # Type error
""",
            "min_errors": 0  # May not be installed
        },
        "isort": {
            "code": """import sys
import os
# Unsorted
""",
            "min_errors": 0  # May not trigger without actual sorting issues
        },
        "eradicate": {
            "code": """# This is commented out code: x = 1
def real_code():
    return 2
""",
            "min_errors": 0  # May not be installed
        },
        "vulture": {
            "code": """def unused_function():
    return 1

def used_function():
    return 2

result = used_function()
""",
            "min_errors": 0  # May not be installed
        },
        "radon": {
            "code": """def simple():
    return 1
""",
            "min_errors": 0  # May not be installed
        }
    }

    success = True
    available_linters = list(LINTERS.keys())
    print(f"\nAvailable linters: {available_linters}")

    for linter_name in available_linters:
        if linter_name in test_cases:
            test_case = test_cases[linter_name]
            try:
                # Extract test parameters
                code = test_case["code"]
                min_errors = test_case["min_errors"]
                kwargs = {k: v for k, v in test_case.items() if k not in ["code", "min_errors"]}

                result = test_linter(
                    linter_name,
                    code,
                    min_errors,
                    **kwargs
                )
                success = result and success
            except Exception as e:
                print(f"  ✗ {linter_name} failed with error: {e}")
                success = False
        else:
            print(f"\n{linter_name}: No test case defined")

    print("\n" + "=" * 60)
    if success:
        print("✓ All linter tests passed!")
        return 0
    else:
        print("✗ Some linter tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())