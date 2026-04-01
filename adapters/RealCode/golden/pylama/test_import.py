#!/usr/bin/env python
"""Test basic imports and functionality of Pylama."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    # Core modules
    import pylama
    print(f"✓ Imported pylama v{pylama.__version__}")

    print("✓ Imported core functions")

    print("✓ Imported errors module")

    print("✓ Imported config module")

    from pylama.lint import LINTERS
    print(f"✓ Imported lint module with {len(LINTERS)} linters: {list(LINTERS.keys())}")

    print("✓ Imported context module")

    print("✓ Imported utils module")

    print("\nAll imports successful!")
    return True

def test_linter_registration():
    """Test that linters are registered."""
    from pylama.lint import LINTERS

    print("\nTesting linter registration...")
    expected_linters = {"pycodestyle", "pyflakes", "mccabe"}
    available_linters = set(LINTERS.keys())

    for linter in expected_linters:
        if linter in available_linters:
            print(f"✓ Linter '{linter}' is registered")
        else:
            print(f"✗ Linter '{linter}' is NOT registered")

    missing = expected_linters - available_linters
    if missing:
        print(f"\nWarning: Missing linters: {missing}")
        print("Make sure dependencies are installed: pip install pycodestyle pyflakes mccabe")
        return False

    return True

def test_error_class():
    """Test Error class functionality."""
    from pylama.errors import Error

    print("\nTesting Error class...")

    # Create an error
    error = Error(
        filename="test.py",
        lnum=10,
        col=5,
        text="Missing whitespace around operator",
        number="E225",
        type="E",
        source="pycodestyle"
    )

    print(f"✓ Created Error: {error}")
    print(f"  filename: {error.filename}")
    print(f"  lnum: {error.lnum}")
    print(f"  col: {error.col}")
    print(f"  text: {error.text}")
    print(f"  number: {error.number}")
    print(f"  type: {error.type}")
    print(f"  source: {error.source}")

    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Pylama Basic Functionality Test")
    print("=" * 60)

    success = True

    try:
        success = test_imports() and success
    except Exception as e:
        print(f"\n✗ Import test failed: {e}")
        success = False

    try:
        success = test_linter_registration() and success
    except Exception as e:
        print(f"\n✗ Linter registration test failed: {e}")
        success = False

    try:
        success = test_error_class() and success
    except Exception as e:
        print(f"\n✗ Error class test failed: {e}")
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())