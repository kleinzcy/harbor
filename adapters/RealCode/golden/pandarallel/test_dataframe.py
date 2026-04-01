import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'tests')

from tests.test_runner import TestRunner

runner = TestRunner()
df = runner._create_numeric_dataframe(10)
print("Numeric DataFrame columns:", df.columns.tolist())
print("dtypes:", df.dtypes)
print("DataFrame:")
print(df)

# Test with string columns
df2 = runner._create_test_dataframe(10, include_strings=True)
print("\n\nDataFrame with strings columns:", df2.columns.tolist())
print("dtypes:", df2.dtypes)
print("DataFrame:")
print(df2)