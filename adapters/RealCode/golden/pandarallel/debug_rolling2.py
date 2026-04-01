import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'tests')

from tests.test_runner import TestRunner

runner = TestRunner()
df = runner._create_test_dataframe(10)
print("Original DataFrame columns:", df.columns.tolist())
print("dtypes:", df.dtypes)

group_col = 'a'
numeric_cols = [col for col in df.columns if col.startswith('col')]
print("Numeric cols:", numeric_cols)

rolling_df = df[[group_col] + numeric_cols].copy()
print("\nRolling DataFrame columns:", rolling_df.columns.tolist())
print("dtypes:", rolling_df.dtypes)

# Test the function
func_str = 'lambda w: w.sum()'
safe_globals = {
    '__builtins__': {
        'abs': abs, 'all': all, 'any': any, 'bool': bool,
        'dict': dict, 'float': float, 'int': int, 'len': len,
        'list': list, 'max': max, 'min': min, 'pow': pow,
        'range': range, 'round': round, 'sorted': sorted,
        'str': str, 'sum': sum, 'tuple': tuple, 'zip': zip,
    }
}
func = eval(func_str, safe_globals)

print("\nTesting rolling apply...")
try:
    result = rolling_df.groupby(group_col).rolling(4).apply(func)
    print("Success!")
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()