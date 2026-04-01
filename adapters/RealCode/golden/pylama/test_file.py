#!/usr/bin/env python
"""Test Pylama functionality on actual code."""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pylama.core import run
from pylama.config import parse_options

def create_test_file(content: str) -> Path:
    """Create a temporary test file."""
    fd, path = tempfile.mkstemp(suffix=".py", prefix="pylama_test_")
    os.close(fd)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return Path(path)

def test_simple_file():
    """Test checking a simple Python file."""
    print("Testing simple file check...")

    # Create a test file with some code
    test_code = """def hello():
    print("Hello, World!")


x = 1  # Good code, no issues expected
"""

    test_file = create_test_file(test_code)
    try:
        # Set up options
        options = parse_options(config=False)
        options.paths = [str(test_file)]
        options.linters = "pycodestyle,pyflakes,mccabe"

        # Run check
        errors = run(options)

        print(f"  Checked file: {test_file}")
        print(f"  Found {len(errors)} errors")

        if errors:
            print("  Errors found:")
            for error in errors:
                print(f"    - Line {error.lnum}: {error.text} ({error.source})")
            return False
        else:
            print("  ✓ No errors found (as expected)")
            return True

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

def test_file_with_issues():
    """Test checking a file with known issues."""
    print("\nTesting file with issues...")

    # Create a test file with style issues
    test_code = """def hello():
    x=1  # Missing spaces around =
    y = 2
    return x+y  # Missing spaces around +


# Unused import
import os

# Undefined variable
print(undefined_var)
"""

    test_file = create_test_file(test_code)
    try:
        # Set up options
        options = parse_options(config=False)
        options.paths = [str(test_file)]
        options.linters = "pycodestyle,pyflakes"

        # Run check
        errors = run(options)

        print(f"  Checked file: {test_file}")
        print(f"  Found {len(errors)} errors")

        if errors:
            print("  ✓ Errors found as expected:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"    - {error.source}: Line {error.lnum}: {error.text}")

            # Count by source
            sources = {}
            for error in errors:
                sources[error.source] = sources.get(error.source, 0) + 1

            print(f"  Error breakdown: {sources}")
            return True
        else:
            print("  ✗ Expected errors but none found")
            return False

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

def test_mccabe_complexity():
    """Test McCabe complexity checking."""
    print("\nTesting McCabe complexity...")

    # Create a test file with complex function
    test_code = """def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        return "very high"
                    return "high"
                return "medium"
            return "low"
        return "very low"
    return "negative"
"""

    test_file = create_test_file(test_code)
    try:
        # Set up options with low complexity threshold
        options = parse_options(config=False)
        options.paths = [str(test_file)]
        options.linters = "mccabe"
        options.max_complexity = 3  # Low threshold to trigger error

        # Run check
        errors = run(options)

        print(f"  Checked file: {test_file}")
        print(f"  Found {len(errors)} complexity errors")

        if errors:
            print("  ✓ Complexity errors found as expected")
            for error in errors:
                print(f"    - {error.text}")
            return True
        else:
            print("  ✗ Expected complexity errors but none found")
            return False

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

def main():
    """Run all functionality tests."""
    print("=" * 60)
    print("Pylama Functionality Tests")
    print("=" * 60)

    success = True

    try:
        success = test_simple_file() and success
    except Exception as e:
        print(f"\n✗ Simple file test failed: {e}")
        import traceback
        traceback.print_exc()
        success = False

    try:
        success = test_file_with_issues() and success
    except Exception as e:
        print(f"\n✗ File with issues test failed: {e}")
        import traceback
        traceback.print_exc()
        success = False

    try:
        success = test_mccabe_complexity() and success
    except Exception as e:
        print(f"\n✗ McCabe complexity test failed: {e}")
        import traceback
        traceback.print_exc()
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ All functionality tests passed!")
        return 0
    else:
        print("✗ Some functionality tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())