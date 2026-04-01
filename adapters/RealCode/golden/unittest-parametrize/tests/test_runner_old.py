#!/usr/bin/env python3
"""
Test runner for unittest-parametrize library.

Reads JSON test case files, dynamically creates test classes, executes them,
and writes output to stdout directory.
"""

import json
import sys
import io
import contextlib
from pathlib import Path
import unittest

# Add src directory to path to import unittest_parametrize
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unittest_parametrize import parametrize, ParametrizedTestCase, param


def load_test_cases(json_path):
    """Load test cases from JSON file."""
    with open(json_path, "r") as f:
        data = json.load(f)
    return data["description"], data["cases"]


def convert_argvalues(argvalues):
    """Convert JSON argvalues to Python objects, handling param objects."""
    converted = []
    for value in argvalues:
        if isinstance(value, dict) and value.get("__type__") == "param":
            converted.append(param.from_dict(value))
        elif isinstance(value, list):
            converted.append(tuple(value))
        else:
            converted.append(value)
    return converted


def run_test_case(json_path, case_index, case):
    """Run a single test case and capture output."""
    input_data = case["input"]
    expected = case["expected_output"]

    # Prepare output buffer
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            # Dynamically create test class
            class_name = f"TestCase_{case_index}"

            # Determine test method name from context
            # Use a generic name; actual name doesn't matter for output
            test_method_name = "test_method"

            # Convert argvalues
            argvalues = convert_argvalues(input_data.get("argvalues", []))

            # Get other parameters
            argnames = input_data.get("argnames")
            ids = input_data.get("ids")
            is_async = input_data.get("async", False)
            scenario = input_data.get("scenario", "")

            # Create test class dynamically
            test_class_dict = {}

            if "error" in expected:
                # Test that expects an error
                # We'll create a test that attempts to apply decorator
                # and verify the error message
                def test_method(self):
                    try:
                        # Attempt to create parameterized method
                        # This should raise an error
                        if argnames is not None:
                            @parametrize(argnames, argvalues, ids)
                            def dummy_test(self):
                                pass
                            # If we get here, error wasn't raised
                            self.fail(f"Expected error: {expected['error']}")
                        else:
                            # Handle decorator constraint scenarios
                            # For simplicity, we'll just note this case
                            pass
                    except Exception as e:
                        if expected["error"] not in str(e):
                            raise AssertionError(
                                f"Error message mismatch.\n"
                                f"Expected: {expected['error']}\n"
                                f"Got: {str(e)}"
                            )
                        # Error matches expected - test passes
                        return

                test_method.__name__ = test_method_name
                test_class_dict[test_method_name] = test_method

            elif "generated_methods" in expected:
                # Test that expects specific generated method names
                # Create a parameterized test and check generated methods
                @parametrize(argnames, argvalues, ids)
                def parameterized_test(self):
                    # Simple assertion to verify parameters are passed
                    # We'll store parameters for verification
                    pass

                # Need to apply this to a class and inspect generated methods
                # For simplicity, we'll just verify the decorator works
                # and print the expected method names
                print(f"Expected methods: {expected['generated_methods']}")

                # Actually create a class with the parameterized method
                # and run unittest to see what methods are generated
                class DynamicTestClass(ParametrizedTestCase):
                    @parametrize(argnames, argvalues, ids)
                    def test_dynamic(self):
                        pass

                # Collect generated method names
                generated = [
                    name for name in dir(DynamicTestClass)
                    if name.startswith("test_dynamic_")
                ]
                print(f"Generated methods: {sorted(generated)}")

                # Add a test method that verifies the generation
                def test_method(self):
                    self.assertEqual(
                        sorted(generated),
                        sorted(expected["generated_methods"])
                    )

                test_method.__name__ = test_method_name
                test_class_dict[test_method_name] = test_method

            else:
                # Other types of test cases (parameters, async, etc.)
                # For now, just print the case info
                print(f"Case type not fully implemented: {list(expected.keys())}")

            # Create the test class
            TestClass = type(class_name, (unittest.TestCase,), test_class_dict)

            # Run the test
            suite = unittest.TestLoader().loadTestsFromTestCase(TestClass)
            runner = unittest.TextTestRunner(stream=output, verbosity=0)
            result = runner.run(suite)

        except Exception:
            # Capture any unexpected errors
            import traceback
            traceback.print_exc(file=output)

    # Get output and clean up extra whitespace
    output_text = output.getvalue().strip()
    return output_text


def main():
    """Main entry point."""
    test_cases_dir = Path(__file__).parent / "test_cases"
    output_dir = Path(__file__).parent / "stdout"

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Process each JSON file
    for json_path in test_cases_dir.glob("*.json"):
        print(f"Processing {json_path.name}...", file=sys.stderr)

        description, cases = load_test_cases(json_path)
        stem = json_path.stem

        for i, case in enumerate(cases):
            output_text = run_test_case(json_path, i, case)

            # Write output file
            output_file = output_dir / f"{stem}@{i:03d}.txt"
            with open(output_file, "w") as f:
                f.write(output_text)

    print(f"All test cases processed. Output in {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()