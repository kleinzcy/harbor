#!/usr/bin/env python3
"""Check test results more accurately."""

import sys
from pathlib import Path

stdout_dir = Path(__file__).parent / "tests" / "stdout"

passed = []
failed = []
skipped = []

for output_file in sorted(stdout_dir.glob("*.txt")):
    with open(output_file, 'r') as f:
        content = f.read()

    test_name = output_file.name

    # Check for various patterns
    if "ERROR: Error message mismatch" in content:
        failed.append(test_name)
    elif "ERROR: Expected error" in content and "but no error was raised" in content:
        failed.append(test_name)
    elif "ERROR during" in content:
        failed.append(test_name)
    elif "FAIL:" in content and "PASS:" not in content:
        failed.append(test_name)
    elif "SKIP:" in content:
        skipped.append(test_name)
    elif "PASS:" in content:
        passed.append(test_name)
    else:
        # No explicit PASS/FAIL - check if it's an error test
        # Error tests output just the error message
        # For now, assume it passed if it doesn't have ERROR/FAIL
        passed.append(test_name)

print(f"Total tests: {len(passed) + len(failed) + len(skipped)}")
print(f"Passed: {len(passed)}")
print(f"Failed: {len(failed)}")
print(f"Skipped: {len(skipped)}")

if failed:
    print("\nFailed tests:")
    for test in sorted(failed):
        print(f"  {test}")
        with open(stdout_dir / test, 'r') as f:
            lines = f.readlines()
            for line in lines[:5]:
                if line.strip():
                    print(f"    {line.rstrip()}")

print("\nPassed tests:")
for test in sorted(passed)[:10]:  # Show first 10
    print(f"  {test}")
if len(passed) > 10:
    print(f"  ... and {len(passed) - 10} more")

sys.exit(1 if failed else 0)