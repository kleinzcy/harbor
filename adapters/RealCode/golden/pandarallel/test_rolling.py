import pandas as pd
import numpy as np

np.random.seed(42)
df = pd.DataFrame({
    'col0': np.random.randn(10),
    'col1': np.random.randn(10),
    'col2': np.random.randn(10),
    'a': np.random.choice(['x', 'y', 'z'], 10),
    'b': np.random.choice(['p', 'q'], 10)
})

print("DataFrame:")
print(df)
print("\ndtypes:", df.dtypes)

# Test rolling sum with numeric_only=True
print("\nTesting rolling sum with numeric_only=True:")
try:
    result = df.groupby('a').rolling(4).apply(lambda w: w.sum(numeric_only=True))
    print("Success:", result)
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()

# Test selecting only numeric columns first
print("\n\nTesting with only numeric columns:")
numeric_cols = ['col0', 'col1', 'col2']
df_numeric = df[numeric_cols].copy()
df_numeric['a'] = df['a']  # Add grouping column back
print("Numeric DataFrame:")
print(df_numeric)

try:
    result = df_numeric.groupby('a').rolling(4).apply(lambda w: w.sum())
    print("Success:", result)
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()