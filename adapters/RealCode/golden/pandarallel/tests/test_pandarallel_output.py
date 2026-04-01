#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandarallel
pandarallel.initialize()

np.random.seed(42)

# Create test dataframe similar to test_runner
def _create_numeric_grouping_dataframe(size=50, cols=3):
    np.random.seed(42)
    data = {
        f'col{i}': np.random.randn(size) for i in range(cols)
    }
    data['group'] = np.random.choice([0, 1, 2], size)
    return pd.DataFrame(data)

df = _create_numeric_grouping_dataframe(50)
print("DataFrame head:")
print(df.head())

# Test serial groupby rolling
print("\n=== Serial groupby rolling ===")
result_serial = df.groupby('group').rolling(4).apply(lambda w: w.sum())
print("Result index:", result_serial.index)
print("Result columns:", result_serial.columns.tolist())
result_serial_reset = result_serial.reset_index()
print("After reset_index(), columns:", result_serial_reset.columns.tolist())
print("First few rows:")
print(result_serial_reset.head(10))

# Test parallel groupby rolling
print("\n=== Parallel groupby rolling ===")
try:
    result_parallel = df.groupby('group').rolling(4).parallel_apply(lambda w: w.sum())
    print("Result index:", result_parallel.index)
    print("Result columns:", result_parallel.columns.tolist())
    result_parallel_reset = result_parallel.reset_index()
    print("After reset_index(), columns:", result_parallel_reset.columns.tolist())
    print("First few rows:")
    print(result_parallel_reset.head(10))
except Exception as e:
    print(f"Error in parallel apply: {e}")
    import traceback
    traceback.print_exc()

# Also test the exact code from test_runner
print("\n=== Testing exact test_runner logic ===")
from test_runner import TestRunner
runner = TestRunner(output_dir="tmp_test")
test_case = {
    "input": {
        "operation": "groupby_rolling",
        "group_col": "a",
        "window": 4,
        "df_size": 50,
        "func": "lambda w: w.sum()"
    }
}
output = runner._run_test_case(test_case)
print("Output (first 500 chars):")
print(output[:500])