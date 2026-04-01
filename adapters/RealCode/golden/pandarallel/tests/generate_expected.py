#!/usr/bin/env python3
"""
Generate expected outputs for test cases by computing serial results.
Updates JSON files in place.
"""
import json
import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ExpectedOutputGenerator:
    """Generates expected outputs for test cases."""

    def __init__(self):
        np.random.seed(42)  # Same seed as TestRunner

    def _create_test_dataframe(self, size: int, cols: int = 3, include_strings: bool = True) -> pd.DataFrame:
        """Create test DataFrame with random data."""
        np.random.seed(42)
        data = {
            f'col{i}': np.random.randn(size) for i in range(cols)
        }
        if include_strings:
            data['a'] = np.random.choice(['x', 'y', 'z'], size)  # For grouping
            data['b'] = np.random.choice(['p', 'q'], size)  # For multi-column grouping
        return pd.DataFrame(data)

    def _create_numeric_dataframe(self, size: int, cols: int = 3) -> pd.DataFrame:
        """Create test DataFrame with only numeric columns."""
        return self._create_test_dataframe(size, cols, include_strings=False)

    def _create_numeric_grouping_dataframe(self, size: int, cols: int = 3) -> pd.DataFrame:
        """Create test DataFrame with numeric grouping column."""
        np.random.seed(42)
        data = {
            f'col{i}': np.random.randn(size) for i in range(cols)
        }
        data['group'] = np.random.choice([0, 1, 2], size)
        return pd.DataFrame(data)

    def _create_test_series(self, size: int) -> pd.Series:
        """Create test Series with random data."""
        np.random.seed(42)
        return pd.Series(np.random.randn(size))

    def _eval_func(self, func_str: str):
        """Safely evaluate a function string."""
        if not func_str.startswith('lambda '):
            raise ValueError(f"Function must start with 'lambda ': {func_str}")
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
        Must match the implementation in test_runner.py.
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
            # Use fixed 10 decimal places without stripping trailing zeros for consistency
            float_format = lambda x: f"{x:.10f}"

            if isinstance(result, pd.Series):
                # Convert to frame with one column named 'value'
                df = pd.DataFrame({'value': result})
                return df.to_csv(index=True, float_format=float_format)
            else:
                return result.to_csv(index=True, float_format=float_format)
        elif isinstance(result, (np.number, np.bool_)):
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
            return repr(result)

    def compute_expected_output(self, test_case: Dict[str, Any]) -> str:
        """
        Compute expected output for a test case using serial operations.
        """
        input_data = test_case.get('input', {})
        operation = input_data.get('operation')

        # For initialization tests (operation is None), output "initialized"
        if operation is None:
            return "initialized"

        # For get_default_workers, we can't know the exact number, keep ">= 1"
        if operation == "get_default_workers":
            # This test expects ">= 1" or similar, we keep original expected output
            # Return placeholder, will be replaced with original
            return test_case.get('expected_output', '>= 1')

        # Get data size
        df_size = input_data.get('df_size', 100)

        if operation == "dataframe_apply":
            df = self._create_numeric_dataframe(df_size)
            func_str = input_data.get('func', 'lambda x: x.sum(numeric_only=True)')
            func = self._eval_func(func_str)
            axis = input_data.get('axis', 0)
            result = df.apply(func, axis=axis)
            return self._result_to_string(result)

        elif operation == "dataframe_applymap":
            df = self._create_numeric_dataframe(df_size)
            func_str = input_data.get('func', 'lambda x: x*2')
            func = self._eval_func(func_str)
            # Use pandas applymap (deprecated in new versions)
            if hasattr(df, 'map'):
                result = df.map(func)
            else:
                result = df.applymap(func)
            return self._result_to_string(result)

        elif operation == "series_apply":
            series = self._create_test_series(df_size)
            func_str = input_data.get('func', 'lambda x: x**2')
            func = self._eval_func(func_str)
            result = series.apply(func)
            return self._result_to_string(result)

        elif operation == "series_map":
            series = self._create_test_series(df_size)
            func_str = input_data.get('func', 'lambda x: x+1')
            func = self._eval_func(func_str)
            result = series.map(func)
            return self._result_to_string(result)

        elif operation == "groupby_apply":
            df = self._create_test_dataframe(df_size)
            group_cols = input_data.get('group_cols', ['a'])
            func_str = input_data.get('func', 'lambda g: g.sum(numeric_only=True)')
            func = self._eval_func(func_str)
            try:
                result = df.groupby(group_cols).apply(func, include_groups=False)
            except TypeError:
                result = df.groupby(group_cols).apply(func)
            result = result.reset_index()
            return self._result_to_string(result)

        elif operation == "series_rolling":
            series = self._create_test_series(df_size)
            window = input_data.get('window', 4)
            func_str = input_data.get('func', 'lambda w: w.mean()')
            func = self._eval_func(func_str)
            result = series.rolling(window).apply(func)
            return self._result_to_string(result)

        elif operation == "groupby_rolling":
            # Note: JSON expects group_col 'a', but we use numeric grouping column 'group'
            # For consistency with test_runner, we use 'group'
            df = self._create_numeric_grouping_dataframe(df_size)
            group_col = 'group'
            window = input_data.get('window', 4)
            func_str = input_data.get('func', 'lambda w: w.sum()')
            func = self._eval_func(func_str)
            result = df.groupby(group_col).rolling(window).apply(func)
            # Reset index for consistent output format
            # Reset with column names for multi-level index
            if isinstance(result.index, pd.MultiIndex):
                result = result.reset_index()
                # Rename index columns to match expected format
                # The first level is 'group' (from groupby), needs to be 'level_0' to match test_runner
                # The second level is unnamed, becomes 'level_1' after reset, needs to be 'index'
                if len(result.columns) >= 1 and result.columns[0] == 'group':
                    result = result.rename(columns={'group': 'level_0'})
                if len(result.columns) >= 2 and result.columns[1] == 'level_1':
                    result = result.rename(columns={'level_1': 'index'})
            else:
                result = result.reset_index()
            return self._result_to_string(result)

        elif operation == "series_expanding":
            series = self._create_test_series(df_size)
            func_str = input_data.get('func', 'lambda w: w.max()')
            func = self._eval_func(func_str)
            result = series.expanding().apply(func)
            return self._result_to_string(result)

        elif operation == "groupby_expanding":
            df = self._create_numeric_grouping_dataframe(df_size)
            group_col = 'group'
            func_str = input_data.get('func', 'lambda w: w.min()')
            func = self._eval_func(func_str)
            result = df.groupby(group_col).expanding().apply(func)
            # Reset index for consistent output format
            # Reset with column names for multi-level index
            if isinstance(result.index, pd.MultiIndex):
                result = result.reset_index()
                # Rename index columns to match expected format
                # The first level is 'group' (from groupby), needs to be 'level_0' to match test_runner
                # The second level is unnamed, becomes 'level_1' after reset, needs to be 'index'
                if len(result.columns) >= 1 and result.columns[0] == 'group':
                    result = result.rename(columns={'group': 'level_0'})
                if len(result.columns) >= 2 and result.columns[1] == 'level_1':
                    result = result.rename(columns={'level_1': 'index'})
            else:
                result = result.reset_index()
            return self._result_to_string(result)

        else:
            # Unknown operation, keep original expected output
            return test_case.get('expected_output', 'success')

    def update_json_file(self, json_path: str):
        """Update expected_output fields in a JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)

        updated = False
        for i, test_case in enumerate(data.get('cases', [])):
            # Skip exception tests (expected_output is error type)
            expected = test_case.get('expected_output', '')
            if expected in ['ZeroDivisionError', 'AttributeError']:
                continue
            # Skip get_default_workers with ">= 1" pattern
            if isinstance(expected, str) and expected.startswith('>='):
                continue
            new_expected = self.compute_expected_output(test_case)
            if new_expected != expected:
                test_case['expected_output'] = new_expected
                updated = True
                print(f"  Case {i}: updated")

        if updated:
            # Write back
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Updated {json_path}")
        else:
            print(f"No changes needed for {json_path}")

    def update_all_files(self, test_cases_dir: str = "test_cases"):
        """Update all JSON files in directory."""
        for filename in os.listdir(test_cases_dir):
            if filename.endswith('.json'):
                json_path = os.path.join(test_cases_dir, filename)
                print(f"Processing {filename}...")
                self.update_json_file(json_path)

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Generate expected outputs for test cases')
    parser.add_argument('--test-dir', default='test_cases', help='Test cases directory')
    parser.add_argument('--file', help='Process specific JSON file')

    args = parser.parse_args()

    generator = ExpectedOutputGenerator()

    if args.file:
        generator.update_json_file(args.file)
    else:
        generator.update_all_files(args.test_dir)

if __name__ == '__main__':
    main()