#!/usr/bin/env python
"""
Test runner for tsfresh test cases.
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# Mapping from test case file to script
SCRIPT_MAPPING = {
    "feature1_extraction": "run_extraction.py",
    "feature2_selection": "run_selection.py",
    "feature3_1_multivariate": "run_extraction.py",
    "feature3_2_irregular": "run_extraction.py",
    "feature4_interface": "run_interface.py",
    "feature5_examples": "run_examples.py",
    "feature6_package": "run_package.py",
}

def run_test_case(test_case_file: Path, case_index: int, case_data: dict):
    """Run a single test case."""
    # Determine which script to use
    test_name = test_case_file.stem
    script_name = SCRIPT_MAPPING.get(test_name)

    if not script_name:
        print(f"No script mapping for {test_name}", file=sys.stderr)
        return False

    script_path = Path("..") / script_name

    if not script_path.exists():
        print(f"Script not found: {script_path}", file=sys.stderr)
        return False

    # Prepare input JSON for the script
    # The script expects the input dict directly
    input_data = case_data.get("input", {})

    # Run script with input as JSON
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"Script failed: {result.stderr}", file=sys.stderr)
            return False

        # Save output to stdout directory
        stdout_dir = Path("stdout")
        stdout_dir.mkdir(exist_ok=True)

        output_file = stdout_dir / f"{test_name}@{case_index:03d}.txt"
        with open(output_file, "w") as f:
            f.write(result.stdout)

        return True

    except subprocess.TimeoutExpired:
        print(f"Script timed out: {script_name}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error running script: {e}", file=sys.stderr)
        return False

def main():
    # Change to tests directory
    tests_dir = Path(__file__).parent
    os.chdir(tests_dir)

    # Find all test case files
    test_cases_dir = Path("test_cases")
    if not test_cases_dir.exists():
        print("test_cases directory not found", file=sys.stderr)
        sys.exit(1)

    test_files = list(test_cases_dir.glob("*.json"))

    if not test_files:
        print("No test case files found", file=sys.stderr)
        sys.exit(1)

    # Run tests
    all_passed = True

    for test_file in sorted(test_files):
        print(f"Processing {test_file.name}...", file=sys.stderr)

        try:
            with open(test_file, "r") as f:
                test_data = json.load(f)

            cases = test_data.get("cases", [])

            for i, case in enumerate(cases):
                print(f"  Case {i}...", file=sys.stderr)
                success = run_test_case(test_file, i, case)
                if not success:
                    all_passed = False
                    print(f"  Case {i} failed", file=sys.stderr)
                else:
                    print(f"  Case {i} passed", file=sys.stderr)

        except Exception as e:
            print(f"Error processing {test_file}: {e}", file=sys.stderr)
            all_passed = False

    if all_passed:
        print("All tests completed successfully", file=sys.stderr)
        sys.exit(0)
    else:
        print("Some tests failed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()