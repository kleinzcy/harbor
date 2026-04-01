#!/usr/bin/env python3
"""Check test results from stdout files."""

import sys
from pathlib import Path

stdout_dir = Path(__file__).parent / "tests" / "stdout"

passed = []
failed = []
skipped = []

for output_file in stdout_dir.glob("*.txt"):
    with open(output_file, 'r') as f:
        content = f.read().strip()

    test_name = output_file.name

    # Check for PASS/FAIL/SKIP keywords
    if "PASS:" in content or "SKIP:" in content:
        if "FAIL:" in content:
            # Both PASS and FAIL - check which comes last
            pass_index = content.find("PASS:")
            fail_index = content.find("FAIL:")
            if fail_index > pass_index:
                failed.append(test_name)
            else:
                passed.append(test_name)
        else:
            if "SKIP:" in content:
                skipped.append(test_name)
            else:
                passed.append(test_name)
    elif "FAIL:" in content:
        failed.append(test_name)
    else:
        # Unknown status
        failed.append(test_name)

print(f"Total tests: {len(passed) + len(failed) + len(skipped)}")
print(f"Passed: {len(passed)}")
print(f"Failed: {len(failed)}")
print(f"Skipped: {len(skipped)}")

if failed:
    print("\nFailed tests:")
    for test in sorted(failed):
        print(f"  {test}")
        # Show first few lines of output
        with open(stdout_dir / test, 'r') as f:
            lines = f.readlines()
            for line in lines[:3]:
                print(f"    {line.rstrip()}")

if skipped:
    print("\nSkipped tests:")
    for test in sorted(skipped):
        print(f"  {test}")

# Exit with error code if any failures
sys.exit(1 if failed else 0)