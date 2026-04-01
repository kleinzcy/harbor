#!/usr/bin/env python3
"""
Validate enhanced test cases against reference implementation.
Compares actual output with expected output and reports results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tests.test_runner import (
    load_test_cases, run_feature1_test, run_feature2_test,
    run_feature3_test, run_feature4_test, run_feature5_test
)

# Map feature file prefixes to test functions
TEST_HANDLERS = {
    'feature1_file_discovery': run_feature1_test,
    'feature2_content_matching': run_feature2_test,
    'feature3_output_formatting': run_feature3_test,
    'feature4_cli': run_feature4_test,
    'feature5_cross_platform': run_feature5_test,
}

def compare_output(actual, expected, case_index, feature_name):
    """Compare actual and expected output, return True if they match."""
    # Simple comparison for now - can be enhanced for more complex types
    if actual == expected:
        return True, None
    else:
        # Try to provide a diff-like message
        return False, f"Case {case_index}: Output mismatch\n  Expected: {expected}\n  Actual: {actual}"

def validate_feature(test_file):
    """Validate all test cases in a feature file."""
    print(f"Validating {test_file.name}...")

    # Determine handler based on filename
    handler = None
    for prefix, h in TEST_HANDLERS.items():
        if test_file.stem.startswith(prefix):
            handler = h
            break

    if not handler:
        print(f"  Warning: No handler for {test_file.name}")
        return 0, 0

    # Load test cases
    try:
        cases = load_test_cases(test_file)
    except Exception as e:
        print(f"  Error loading {test_file}: {e}")
        return 0, 0

    passed = 0
    failed = 0

    for i, case in enumerate(cases):
        try:
            input_data = case['input']
            expected_output = case['expected_output']
            actual_output = handler(input_data)

            # Compare
            is_match, error_msg = compare_output(actual_output, expected_output, i, test_file.stem)

            if is_match:
                passed += 1
                print(f"  Case {i}: PASS")
            else:
                failed += 1
                print(f"  Case {i}: FAIL - {error_msg}")

        except Exception as e:
            failed += 1
            print(f"  Case {i}: ERROR - {e}")

    return passed, failed

def main():
    """Main validation function."""
    enhanced_dir = Path('tests/enhanced_test_cases')

    if not enhanced_dir.exists():
        print(f"Enhanced test cases directory not found: {enhanced_dir}")
        sys.exit(1)

    print("=" * 60)
    print("Validating Enhanced Test Cases")
    print("=" * 60)

    total_passed = 0
    total_failed = 0

    # Process each enhanced test file
    for test_file in sorted(enhanced_dir.glob('*.json')):
        print()
        passed, failed = validate_feature(test_file)
        total_passed += passed
        total_failed += failed

    print("\n" + "=" * 60)
    print("Validation Summary:")
    print(f"  Total test cases: {total_passed + total_failed}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print("=" * 60)

    if total_failed > 0:
        print("\n❌ Some test cases failed.")
        sys.exit(1)
    else:
        print("\n✅ All test cases passed!")
        sys.exit(0)

if __name__ == '__main__':
    main()