#!/usr/bin/env python3
"""
Test runner for pysonDB-v2.

Executes all test cases from tests/test_cases/ and saves outputs
to tests/stdout/ as individual .txt files.

Test cases within each file are executed sequentially with shared state.
"""
import json
import sys
from typing import Dict, Any, List
from pathlib import Path

# Add parent directory to path to import scripts
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_operation import TestRunner


class TestFileRunner:
    """Runner for a single test file with sequential test cases."""

    def __init__(self, test_file: Path):
        self.test_file = test_file
        self.runner = TestRunner()
        self.variables = {}  # Store values from previous test cases
        self.results = []  # Store results for each test case

    def run_all_cases(self) -> List[str]:
        """Run all test cases in this file and return outputs."""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)

        cases = test_data.get('cases', [])
        outputs = []

        for i, case in enumerate(cases):
            case_input = case.get('input', {}).copy()

            # Replace variables in input
            self._replace_variables(case_input)

            # Run test case
            result = self.runner.run(case_input)

            # Extract variables from result for future test cases
            self._extract_variables(result, i)

            # Format output
            output = json.dumps(result, indent=2)
            outputs.append(output)

            # Store result
            self.results.append(result)

        return outputs

    def _replace_variables(self, case_input: Dict[str, Any]) -> None:
        """Replace variable placeholders in case input with actual values."""
        # Handle ID replacement for feature1 tests
        # If input has an 'id' field and we have a stored 'last_id', use it
        if 'id' in case_input and 'last_id' in self.variables:
            case_input['id'] = self.variables['last_id']

        # More general variable replacement could be added here
        # For now, just handle the specific case

    def _extract_variables(self, result: Dict[str, Any], case_index: int) -> None:
        """Extract variables from result for use in future test cases."""
        # Store the last generated ID for feature1 tests
        if 'id' in result:
            self.variables['last_id'] = result['id']

        # Store other variables as needed
        if 'merged_keys' in result:
            self.variables['merged_keys'] = result['merged_keys']


def run_all_tests() -> None:
    """Run all test cases and save outputs."""
    test_cases_dir = Path(__file__).parent / 'test_cases'
    output_dir = Path(__file__).parent / 'stdout'

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Clear previous outputs
    for file in output_dir.glob('*.txt'):
        file.unlink()

    print(f"Test cases directory: {test_cases_dir}")
    print(f"Output directory: {output_dir}")
    print()

    total_cases = 0

    # Process each test case file
    for test_file in sorted(test_cases_dir.glob('*.json')):
        print(f"Processing test file: {test_file.name}")

        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  Error loading {test_file}: {e}")
            continue

        cases = test_data.get('cases', [])
        print(f"  Found {len(cases)} test cases")

        # Create runner for this test file
        file_runner = TestFileRunner(test_file)
        outputs = file_runner.run_all_cases()

        # Save outputs
        for i, output in enumerate(outputs):
            total_cases += 1

            # Generate output filename
            filename_stem = test_file.stem
            output_filename = f"{filename_stem}@{i:03d}.txt"
            output_path = output_dir / output_filename

            # Save output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)

            # Validate output is valid JSON
            try:
                json.loads(output)
                print(f"    Case {i}: ✓ Output saved to {output_filename}")
            except json.JSONDecodeError:
                print(f"    Case {i}: ⚠ Output is not valid JSON in {output_filename}")

    print()
    print("Test suite completed.")
    print(f"Total test cases run: {total_cases}")
    print(f"Outputs saved to: {output_dir}")


if __name__ == '__main__':
    run_all_tests()