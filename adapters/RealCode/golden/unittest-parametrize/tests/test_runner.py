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


def run_error_case(input_data, expected_error):
    """Run a test case that expects an error.

    Returns output string containing error message if matches expected,
    otherwise includes assertion error.
    """
    output = io.StringIO()

    try:
        # Extract relevant input data
        argnames = input_data.get("argnames")
        argvalues = convert_argvalues(input_data.get("argvalues", []))
        ids = input_data.get("ids")
        scenario = input_data.get("scenario", "")

        if scenario == "parametrize not outermost":
            # Test that @parametrize must be outermost
            # Apply mock.patch decorator first, then parametrize
            import unittest.mock

            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                try:
                    class TestClass(ParametrizedTestCase):
                        @unittest.mock.patch('builtins.print')
                        @parametrize("x", [1, 2])
                        def test_method(self, mock_print):
                            pass
                except RuntimeError as e:
                    print(str(e))
            return output.getvalue()

        elif scenario == "multiple parametrize decorators":
            # Test stacking prevention
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                try:
                    class TestClass(ParametrizedTestCase):
                        @parametrize("x", [1])
                        @parametrize("y", [2])
                        def test_method(self):
                            pass
                except RuntimeError as e:
                    print(str(e))
            return output.getvalue()

        elif scenario == "duplicate generated method name":
            # Test duplicate method name detection
            # Create a class with existing method test_something_0
            # then add a parameterized method test_something that would generate same name
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                try:
                    # Create a class with existing method
                    class TestClass(ParametrizedTestCase):
                        def test_something_0(self):
                            pass

                    # Now add a parameterized method test_something
                    # We need to apply decorator and add to class
                    # This is tricky because __init_subclass__ already ran.
                    # Instead, create a new class with both methods
                    class TestClass2(ParametrizedTestCase):
                        def test_something_0(self):
                            pass

                        @parametrize("x", [1])
                        def test_something(self):
                            pass
                except ValueError as e:
                    print(str(e))
            return output.getvalue()

        # General error case - attempt to apply decorator
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            try:
                class TestClass(ParametrizedTestCase):
                    @parametrize(argnames, argvalues, ids)
                    def test_method(self):
                        pass
            except Exception as e:
                print(str(e))

    except Exception as e:
        error_msg = str(e)
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            print(error_msg)

    return output.getvalue()


def run_generation_case(input_data, expected_methods):
    """Run a test case that expects specific generated method names.

    Returns output string with generated method names.
    """
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            argnames = input_data.get("argnames")
            argvalues = convert_argvalues(input_data.get("argvalues", []))
            ids = input_data.get("ids")
            is_async = input_data.get("async", False)

            # Determine base name from first expected method
            # Remove trailing _X where X is numeric or custom ID
            if not expected_methods:
                # No expected methods - use a default name
                base_name = "test_method"
            else:
                base_name = expected_methods[0].rsplit("_", 1)[0]

            # Create a function with the base name
            # Use exec to create function with correct __code__.co_name
            if is_async:
                func_template = f"async def {base_name}(self):\n    pass"
            else:
                func_template = f"def {base_name}(self):\n    pass"

            namespace = {}
            exec(func_template, {}, namespace)
            test_func = namespace[base_name]

            # Apply parametrize decorator
            decorated = parametrize(argnames, argvalues, ids)(test_func)

            # Create a class with the decorated method as attribute
            # This will trigger __init_subclass__ processing
            DynamicTest = type(
                'DynamicTest',
                (ParametrizedTestCase,),
                {base_name: decorated}
            )

            # Now the class should have generated methods
            # Collect generated method names
            generated = []
            for name in dir(DynamicTest):
                if name.startswith("test_"):
                    generated.append(name)

            # Filter to only methods that start with base_name + "_"
            filtered = [name for name in generated if name.startswith(base_name + "_")]

            # If no prefix matches, use all test_* methods
            if not filtered:
                filtered = generated

            # Output only the generated methods (actual program output)
            print(sorted(filtered))

        except Exception as e:
            print(str(e))

    return output.getvalue()


def run_parameters_case(input_data, expected_parameters):
    """Run a test case that expects specific parameter values.

    Returns output string with parameter values.
    """
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            argnames = input_data.get("argnames")
            argvalues = convert_argvalues(input_data.get("argvalues", []))

            # Create a test that captures parameters
            captured_params = []

            class ParamCaptureTest(ParametrizedTestCase):
                @parametrize(argnames, argvalues)
                def test_capture(self, *args, **kwargs):
                    # Store parameters for verification
                    params = {}
                    if kwargs:
                        params.update(kwargs)
                    else:
                        # Map by position
                        for i, name in enumerate(argnames.split(",") if isinstance(argnames, str) else argnames):
                            if i < len(args):
                                params[name.strip()] = args[i]
                    captured_params.append(params)

            # Run the test
            suite = unittest.TestLoader().loadTestsFromTestCase(ParamCaptureTest)
            runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0)
            runner.run(suite)

            # Output only the captured parameters (actual program output)
            print(captured_params)

        except Exception as e:
            print(str(e))

    return output.getvalue()


def run_async_case(input_data, expected_output):
    """Run a test case for async methods.

    Returns output string.
    """
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            argnames = input_data.get("argnames")
            argvalues = convert_argvalues(input_data.get("argvalues", []))
            ids = input_data.get("ids")

            # Create async test class
            class AsyncTest(ParametrizedTestCase):
                @parametrize(argnames, argvalues, ids)
                async def test_async_method(self):
                    pass

            # Check if methods were generated
            generated = [name for name in dir(AsyncTest) if name.startswith("test_async_method_")]

            # Output only the generated async methods (actual program output)
            print(generated)

        except Exception as e:
            print(str(e))

    return output.getvalue()


def run_error_enhancement_case(input_data, expected_error_contains):
    """Run error enhancement test case for Python 3.11+.

    Returns output string.
    """
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            import sys
            python_version = input_data.get("python_version", "3.11")
            required_version = tuple(map(int, python_version.split(".")))

            # Check if we're running on the required Python version
            if sys.version_info < required_version:
                print(f"SKIP: Python {sys.version_info.major}.{sys.version_info.minor} "
                      f"< {python_version}, error enhancement not available")
                return output.getvalue()

            argnames = input_data["argnames"]
            argvalues = convert_argvalues(input_data["argvalues"])
            test_assertion = input_data["test_assertion"]

            # Parse argnames to get parameter names
            if isinstance(argnames, str):
                param_names = [name.strip() for name in argnames.split(",")]
            else:
                param_names = list(argnames)

            # Create test method dynamically
            # We need to create a function that uses the assertion
            # The assertion is a string like "self.assertEqual(x**2, expected)"
            # We'll create a function that evals it in the right context
            param_str = ", ".join(param_names)

            # Create the test method source code
            source = f'''def test_method(self, {param_str}):
    {test_assertion}
'''

            # Compile and exec to create the function
            code = compile(source, '<string>', 'exec')
            namespace = {}
            exec(code, {}, namespace)
            test_func = namespace['test_method']

            # Create a test class with the parameterized method
            # We need to do this dynamically because we need to apply the decorator
            # to a method that's defined in the class body
            class_dict = {}

            # Apply parametrize decorator to the function
            decorated = parametrize(argnames, argvalues)(test_func)
            class_dict['test_method'] = decorated

            # Create the class
            ErrorTest = type('ErrorTest', (ParametrizedTestCase,), class_dict)

            # Now run the tests
            suite = unittest.TestLoader().loadTestsFromTestCase(ErrorTest)

            # Capture test output
            result_stream = io.StringIO()
            runner = unittest.TextTestRunner(stream=result_stream, verbosity=0)
            result = runner.run(suite)

            # Output only the actual program output (failure traceback if any)
            if result.failures:
                print(result.failures[0][1])
            else:
                # No failures - output test runner output
                print(result_stream.getvalue())

        except Exception as e:
            print(str(e))

    return output.getvalue()


def run_compatibility_case(input_data, expected_output):
    """Run compatibility test case.

    Returns output string.
    """
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            # Handle empty argvalues case
            if "argnames" in input_data and "argvalues" in input_data:
                argnames = input_data["argnames"]
                argvalues = convert_argvalues(input_data["argvalues"])

                class EmptyTest(ParametrizedTestCase):
                    @parametrize(argnames, argvalues)
                    def test_method(self):
                        pass

                # Check that original method was removed
                methods = [name for name in dir(EmptyTest) if name.startswith("test_")]
                # Output only the methods list (actual program output)
                print(methods)

            # Handle mixed test suite case - MixedTestSuite
            elif "test_class" in input_data and input_data["test_class"] == "MixedTestSuite":
                # Create a test class with mixed parameterized and traditional tests
                class MixedTestSuite(ParametrizedTestCase):
                    def test_traditional(self):
                        self.assertTrue(True)

                    @parametrize("x", [1, 2, 3])
                    def test_parametrized(self, x):
                        self.assertIsInstance(x, int)

                    def test_another_traditional(self):
                        self.assertFalse(False)

                # Count test methods
                test_methods = []
                for name in dir(MixedTestSuite):
                    if name.startswith("test_"):
                        test_methods.append(name)

                # Count should be: 2 traditional + 3 parameterized = 5
                # But parameterized methods have suffixes (_0, _1, _2)
                # So we expect: test_traditional, test_parametrized_0, test_parametrized_1,
                # test_parametrized_2, test_another_traditional
                # Run the tests to verify they work
                suite = unittest.TestLoader().loadTestsFromTestCase(MixedTestSuite)
                result_stream = io.StringIO()
                runner = unittest.TextTestRunner(stream=result_stream, verbosity=0)
                result = runner.run(suite)

                # Output only the test runner output (actual program output)
                print(result_stream.getvalue())

            # Handle mixed test suite case - MixedPrefix
            elif "test_class" in input_data and input_data["test_class"] == "MixedPrefix":
                # Create a test class with mixed parameterized and traditional tests
                class MixedPrefix(ParametrizedTestCase):
                    def test_one(self):
                        self.assertTrue(True)

                    @parametrize("x", [1, 2, 3])
                    def test_two(self, x):
                        self.assertIsInstance(x, int)

                    def test_three(self):
                        self.assertFalse(False)

                # Run the tests
                suite = unittest.TestLoader().loadTestsFromTestCase(MixedPrefix)
                result_stream = io.StringIO()
                runner = unittest.TextTestRunner(stream=result_stream, verbosity=0)
                result = runner.run(suite)

                # Output only the test runner output (actual program output)
                print(result_stream.getvalue())

        except Exception as e:
            print(str(e))

    return output.getvalue()


def run_test_case(json_path, case_index, case):
    """Run a single test case and return output string."""
    input_data = case["input"]
    expected = case["expected_output"]

    # Dispatch based on expected output keys
    if "error" in expected:
        return run_error_case(input_data, expected["error"])

    elif "generated_methods" in expected:
        return run_generation_case(input_data, expected["generated_methods"])

    elif "parameters" in expected:
        return run_parameters_case(input_data, expected["parameters"])

    elif "async" in expected:
        return run_async_case(input_data, expected)

    elif "error_contains" in expected:
        return run_error_enhancement_case(input_data, expected["error_contains"])

    elif "runs_with" in expected or "non_parametrized_work" in expected or "original_method_removed" in expected:
        return run_compatibility_case(input_data, expected)

    else:
        # Unknown case type
        return f"Unknown test case type: {list(expected.keys())}"


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
                f.write(output_text.strip())

    print(f"All test cases processed. Output in {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()