#!/usr/bin/env python3
import pandas as pd
import numpy as np

np.random.seed(42)

# Create test dataframe similar to test_runner
def _create_numeric_grouping_dataframe(size=150, cols=3):
    np.random.seed(42)
    data = {
        f'col{i}': np.random.randn(size) for i in range(cols)
    }
    data['group'] = np.random.choice([0, 1, 2], size)
    return pd.DataFrame(data)

df = _create_numeric_grouping_dataframe(50)
print("DataFrame head:")
print(df.head())
print("\nGroupBy rolling result:")
result = df.groupby('group').rolling(4).apply(lambda w: w.sum())
print("Result type:", type(result))
print("Result index:", result.index)
print("Result head (before reset):")
print(result.head(20))

# Reset index
result_reset = result.reset_index()
print("\nAfter reset_index():")
print("Columns:", result_reset.columns.tolist())
print("Head:")
print(result_reset.head(20))

# Check column names
print("\nChecking column names after reset:")
for i, col in enumerate(result_reset.columns):
    print(f"  Column {i}: {col} (type: {type(col)})")

# Try rename logic
if len(result_reset.columns) >= 2 and result_reset.columns[0] == 'level_0':
    print("\nRenaming level_0 to 'group'")
    result_renamed = result_reset.rename(columns={'level_0': 'group'})
    print("Columns after rename:", result_renamed.columns.tolist())

if len(result_reset.columns) >= 3 and result_reset.columns[1] == 'level_1':
    print("Renaming level_1 to 'index'")
    result_renamed = result_renamed.rename(columns={'level_1': 'index'}) if 'result_renamed' in locals() else result_reset.rename(columns={'level_1': 'index'})
    print("Columns after rename:", result_renamed.columns.tolist())