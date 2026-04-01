"""
Test runner for Pandarallel.

Reads JSON test cases and executes them, writing output to stdout directory.
"""
import json
import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any
import importlib.util

# Add parent directory to path to import pandarallel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def import_pandarallel():
    """Dynamically import pandarallel module."""
    try:
        import pandarallel
        return pandarallel
    except ImportError:
        # Try to import directly
        spec = importlib.util.spec_from_file_location(
            "pandarallel",
            os.path.join(os.path.dirname(__file__), "..", "pandarallel", "__init__.py")
        )
        pandarallel = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pandarallel)
        return pandarallel


class TestRunner:
    """Runs test cases from JSON files."""

    def __init__(self, output_dir: str = "stdout"):
        """
        Initialize test runner.

        Args:
            output_dir: Directory to write output files
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Import pandarallel
        self.pandarallel = import_pandarallel()
        # Initialize pandarallel with default settings
        self.pandarallel.initialize()
        self.failures = 0

    def _create_test_dataframe(self, size: int, cols: int = 3, include_strings: bool = True) -> pd.DataFrame:
        """
        Create test DataFrame with random data.

        Args:
            size: Number of rows
            cols: Number of columns
            include_strings: Whether to include string columns for grouping

        Returns:
            pd.DataFrame: Test DataFrame
        """
        np.random.seed(42)
        data = {
            f'col{i}': np.random.randn(size) for i in range(cols)
        }
        if include_strings:
            data['a'] = np.random.choice(['x', 'y', 'z'], size)  # For grouping
            data['b'] = np.random.choice(['p', 'q'], size)  # For multi-column grouping
        return pd.DataFrame(data)

    def _create_numeric_dataframe(self, size: int, cols: int = 3) -> pd.DataFrame:
        """
        Create test DataFrame with only numeric columns.
        """
        return self._create_test_dataframe(size, cols, include_strings=False)

    def _create_grouping_dataframe(self, size: int, cols: int = 3) -> pd.DataFrame:
        """
        Create test DataFrame with string grouping columns and numeric data columns.
        """
        return self._create_test_dataframe(size, cols, include_strings=True)

    def _create_numeric_grouping_dataframe(self, size: int, cols: int = 3) -> pd.DataFrame:
        """
        Create test DataFrame with numeric grouping column and numeric data columns.
        For rolling/expanding tests that can't handle string columns.
        """
        np.random.seed(42)
        data = {
            f'col{i}': np.random.randn(size) for i in range(cols)
        }
        # Create numeric grouping column (0, 1, 2)
        data['group'] = np.random.choice([0, 1, 2], size)
        return pd.DataFrame(data)

    def _create_test_series(self, size: int) -> pd.Series:
        """
        Create test Series with random data.

        Args:
            size: Number of elements

        Returns:
            pd.Series: Test Series
        """
        np.random.seed(42)
        return pd.Series(np.random.randn(size))

    def _eval_func(self, func_str: str):
        """
        Safely evaluate a function string.

        Args:
            func_str: Function as string (e.g., "lambda x: x.sum()")

        Returns:
            Callable: Function
        """
        # For security, only allow simple lambda expressions
        if not func_str.startswith('lambda '):
            raise ValueError(f"Function must start with 'lambda ': {func_str}")

        # Use eval with restricted globals
        safe_globals = {
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'bool': bool,
                'dict': dict, 'float': float, 'int': int, 'len': len,
                'list': list, 'max': max, 'min': min, 'pow': pow,
                'range': range, 'round': round, 'sorted': sorted,
                'str': str, 'sum': sum, 'tuple': tuple, 'zip': zip,
            }
        }
        return eval(func_str, safe_globals)

    def _result_to_string(self, result):
        """
        Convert a pandas result (DataFrame, Series, scalar) to a stable string representation.

        Args:
            result: pandas DataFrame, Series, or scalar

        Returns:
            str: Stable string representation
        """
        import pandas as pd
        import numpy as np

        if isinstance(result, (pd.DataFrame, pd.Series)):
            # Sort index and columns for consistency
            if isinstance(result, pd.DataFrame):
                # Don't sort columns to avoid issues with mixed types
                # Just ensure index is sorted if needed
                if not result.index.is_monotonic_increasing:
                    result = result.sort_index()

                # Reset index for DataFrames with index (e.g., groupby results)
                # This ensures consistent CSV format with index as columns
                # For test consistency, always reset index for DataFrames
                # But skip if DataFrame already has an 'index' column (e.g., from groupby operations)
                if 'index' not in result.columns:
                    result = result.reset_index()
            elif isinstance(result, pd.Series):
                if not result.index.is_monotonic_increasing:
                    result = result.sort_index()

            # Use to_csv with fixed precision for floats
            # Set float_format to avoid scientific notation differences
            # Use fixed 10 decimal places without stripping trailing zeros for consistency
            float_format = lambda x: f"{x:.10f}"

            # For Series, ensure we handle index properly
            if isinstance(result, pd.Series):
                # Convert to frame with one column named 'value'
                df = pd.DataFrame({'value': result})
                return df.to_csv(index=True, float_format=float_format)
            else:
                return result.to_csv(index=True, float_format=float_format)
        elif isinstance(result, (np.number, np.bool_)):
            # Convert numpy scalar to Python scalar
            result = result.item()
            if isinstance(result, float):
                return f"{result:.10f}"
            else:
                return str(result)
        elif isinstance(result, (int, float, bool, str)):
            if isinstance(result, float):
                return f"{result:.10f}"
            else:
                return str(result)
        else:
            # Fallback to repr
            return repr(result)

    def _run_test_case(self, test_case: Dict[str, Any]) -> str:
        """
        Run a single test case.

        Args:
            test_case: Test case dictionary

        Returns:
            str: Output string (should match expected_output format)
        """
        input_data = test_case.get('input', {})
        operation = input_data.get('operation')

        try:
            # Initialize pandarallel with test parameters
            nb_workers = input_data.get('nb_workers')
            progress_bar = input_data.get('progress_bar', True)
            verbose = input_data.get('verbose', 0)
            use_memory_fs = input_data.get('use_memory_fs')

            # If no operation specified, just test initialization
            if operation is None:
                # Filter out None values for initialize
                init_kwargs = {}
                if nb_workers is not None:
                    init_kwargs['nb_workers'] = nb_workers
                if progress_bar is not None:
                    init_kwargs['progress_bar'] = progress_bar
                if verbose is not None:
                    init_kwargs['verbose'] = verbose
                if use_memory_fs is not None:
                    init_kwargs['use_memory_fs'] = use_memory_fs

                self.pandarallel.initialize(**init_kwargs)
                return "initialized"

            # Filter out None values for initialize
            init_kwargs = {}
            if nb_workers is not None:
                init_kwargs['nb_workers'] = nb_workers
            if progress_bar is not None:
                init_kwargs['progress_bar'] = progress_bar
            if verbose is not None:
                init_kwargs['verbose'] = verbose
            if use_memory_fs is not None:
                init_kwargs['use_memory_fs'] = use_memory_fs

            self.pandarallel.initialize(**init_kwargs)

            # Execute based on operation type
            if operation == "get_default_workers":
                config = self.pandarallel.PandarallelConfig()
                nb_workers = config.nb_workers
                return str(nb_workers)

            # Get data size
            df_size = input_data.get('df_size', 100)

            if operation == "dataframe_apply":
                df = self._create_numeric_dataframe(df_size)
                func_str = input_data.get('func', 'lambda x: x.sum(numeric_only=True)')
                func = self._eval_func(func_str)
                axis = input_data.get('axis', 0)

                # Run parallel apply
                result = df.parallel_apply(func, axis=axis)
                return self._result_to_string(result)

            elif operation == "dataframe_applymap":
                df = self._create_numeric_dataframe(df_size)
                func_str = input_data.get('func', 'lambda x: x*2')
                func = self._eval_func(func_str)

                # Run parallel applymap
                result = df.parallel_applymap(func)
                return self._result_to_string(result)

            elif operation == "series_apply":
                series = self._create_test_series(df_size)
                func_str = input_data.get('func', 'lambda x: x**2')
                func = self._eval_func(func_str)

                # Run parallel apply
                result = series.parallel_apply(func)
                return self._result_to_string(result)

            elif operation == "series_map":
                series = self._create_test_series(df_size)
                func_str = input_data.get('func', 'lambda x: x+1')
                func = self._eval_func(func_str)

                # Run parallel map
                result = series.parallel_map(func)
                return self._result_to_string(result)

            elif operation == "groupby_apply":
                df = self._create_test_dataframe(df_size)
                group_cols = input_data.get('group_cols', ['a'])
                func_str = input_data.get('func', 'lambda g: g.sum(numeric_only=True)')
                func = self._eval_func(func_str)

                # Run parallel groupby apply
                result = df.groupby(group_cols).parallel_apply(func)
                # Reset index for consistent output format
                result = result.reset_index()
                return self._result_to_string(result)

            elif operation == "series_rolling":
                series = self._create_test_series(df_size)
                window = input_data.get('window', 4)
                func_str = input_data.get('func', 'lambda w: w.mean()')
                func = self._eval_func(func_str)

                # Run parallel rolling apply
                result = series.rolling(window).parallel_apply(func)
                return self._result_to_string(result)

            elif operation == "groupby_rolling":
                # Use numeric grouping column for rolling tests
                df = self._create_numeric_grouping_dataframe(df_size)
                group_col = 'group'  # Use numeric grouping column
                window = input_data.get('window', 4)
                func_str = input_data.get('func', 'lambda w: w.sum()')
                func = self._eval_func(func_str)

                # Run parallel groupby rolling apply
                result = df.groupby(group_col).rolling(window).parallel_apply(func)
                # Reset index for consistent output format
                # Reset with column names for multi-level index
                if isinstance(result.index, pd.MultiIndex):
                    result = result.reset_index()
                    # Rename index columns to match expected format
                    # The first level may be 'group' (from groupby) or unnamed
                    # We need 'level_0' and 'index' columns to match expected output
                    if len(result.columns) >= 1 and result.columns[0] == 'group':
                        result = result.rename(columns={'group': 'level_0'})
                    elif len(result.columns) >= 1 and result.columns[0] == 'level_0':
                        # Already correct
                        pass
                    if len(result.columns) >= 2 and result.columns[1] == 'level_1':
                        result = result.rename(columns={'level_1': 'index'})
                else:
                    result = result.reset_index()
                return self._result_to_string(result)

            elif operation == "series_expanding":
                series = self._create_test_series(df_size)
                func_str = input_data.get('func', 'lambda w: w.max()')
                func = self._eval_func(func_str)

                # Run parallel expanding apply
                result = series.expanding().parallel_apply(func)
                return self._result_to_string(result)

            elif operation == "groupby_expanding":
                # Use numeric grouping column for expanding tests
                df = self._create_numeric_grouping_dataframe(df_size)
                group_col = 'group'  # Use numeric grouping column
                func_str = input_data.get('func', 'lambda w: w.min()')
                func = self._eval_func(func_str)

                # Run parallel groupby expanding apply
                result = df.groupby(group_col).expanding().parallel_apply(func)
                # Reset index for consistent output format
                # Reset with column names for multi-level index
                if isinstance(result.index, pd.MultiIndex):
                    result = result.reset_index()
                    # Rename index columns to match expected format
                    # The first level may be 'group' (from groupby) or unnamed
                    # We need 'level_0' and 'index' columns to match expected output
                    if len(result.columns) >= 1 and result.columns[0] == 'group':
                        result = result.rename(columns={'group': 'level_0'})
                    elif len(result.columns) >= 1 and result.columns[0] == 'level_0':
                        # Already correct
                        pass
                    if len(result.columns) >= 2 and result.columns[1] == 'level_1':
                        result = result.rename(columns={'level_1': 'index'})
                else:
                    result = result.reset_index()
                return self._result_to_string(result)

            else:
                return f"FAIL: Unknown operation: {operation}"

        except Exception as e:
            # Check if this was an expected error
            expected_output = test_case.get('expected_output', 'success')
            if expected_output == type(e).__name__:
                return expected_output
            else:
                return f"FAIL: {type(e).__name__}: {str(e)}"

    def run_test_file(self, json_file: str):
        """
        Run all test cases in a JSON file.

        Args:
            json_file: Path to JSON test file
        """
        try:
            with open(json_file, 'r') as f:
                test_data = json.load(f)
        except Exception as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)
            return

        description = test_data.get('description', 'No description')
        cases = test_data.get('cases', [])

        print(f"Running {json_file}: {description}")
        print(f"  {len(cases)} test case(s)")

        # Run each test case
        for i, test_case in enumerate(cases):
            output = self._run_test_case(test_case)

            # Write output to file
            filename_stem = os.path.splitext(os.path.basename(json_file))[0]
            output_file = os.path.join(
                self.output_dir,
                f"{filename_stem}@{str(i).zfill(3)}.txt"
            )

            with open(output_file, 'w') as f:
                f.write(output)

            # Print status
            expected = test_case.get('expected_output', 'success')
            # Check if output matches expected
            if expected.startswith('>='):
                # Numerical comparison
                try:
                    min_value = int(expected.split('>=')[1].strip())
                    output_value = int(output.strip())
                    matches = output_value >= min_value
                except Exception:
                    matches = False
            else:
                # Allow substring match for exception class names (workers may wrap as RuntimeError).
                _exception_specs = (
                    "ZeroDivisionError",
                    "AttributeError",
                    "ValueError",
                    "TypeError",
                    "KeyError",
                    "RuntimeError",
                )
                if expected in _exception_specs:
                    matches = output == expected or expected in output
                else:
                    matches = output == expected

            if not matches and not expected.startswith('>='):
                print(f"    DEBUG: output length {len(output)}, expected length {len(expected)}")
                print(f"    DEBUG: output first 50 chars: {repr(output[:50])}")
                print(f"    DEBUG: expected first 50 chars: {repr(expected[:50])}")

            status = "✓" if matches else "✗"
            if not matches:
                self.failures += 1
            print(f"  Case {i}: {status} -> {output_file}")

    def run_all_tests(self, test_cases_dir: str = "test_cases"):
        """
        Run all test files in a directory.

        Args:
            test_cases_dir: Directory containing JSON test files
        """
        test_files = []
        for file in os.listdir(test_cases_dir):
            if file.endswith('.json'):
                test_files.append(os.path.join(test_cases_dir, file))

        test_files.sort()  # Run in consistent order

        print(f"Found {len(test_files)} test files")

        for test_file in test_files:
            self.run_test_file(test_file)
            print()  # Blank line between files


def _tests_script_dir() -> str:
    """Directory containing this script (the tests/ folder)."""
    return os.path.dirname(os.path.abspath(__file__))


def _resolve_test_path(path: str) -> str:
    """
    Resolve paths relative to tests/ so the runner works no matter the shell cwd.
    Absolute paths are left unchanged.
    """
    if not path:
        return path
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(_tests_script_dir(), path))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Run Pandarallel tests')
    parser.add_argument('--test-file', help='Run specific test file')
    parser.add_argument(
        '--test-dir',
        default='test_cases',
        help='Test cases directory (relative to tests/ unless absolute)',
    )
    parser.add_argument(
        '--output-dir',
        default='stdout',
        help='Output directory (relative to tests/ unless absolute)',
    )

    args = parser.parse_args()

    args.output_dir = _resolve_test_path(args.output_dir)
    args.test_dir = _resolve_test_path(args.test_dir)

    runner = TestRunner(output_dir=args.output_dir)

    if args.test_file:
        test_file = _resolve_test_path(args.test_file)
        runner.run_test_file(test_file)
    else:
        if not os.path.isdir(args.test_dir):
            print(
                f"Error: test directory not found: {args.test_dir}\n"
                f"  Use --test-dir test_cases or --test-dir enhanced_test_cases (under tests/).",
                file=sys.stderr,
            )
            sys.exit(2)
        runner.run_all_tests(args.test_dir)

    if runner.failures:
        print(f"\nFAILED: {runner.failures} case(s) did not match expected output.", file=sys.stderr)
        sys.exit(1)
    print("\nAll test cases passed.")


if __name__ == '__main__':
    main()