import pandas as pd
print(f"pandas version: {pd.__version__}")
print(f"hasattr(pd.DataFrame, 'applymap'): {hasattr(pd.DataFrame, 'applymap')}")
print(f"hasattr(pd.DataFrame, 'map'): {hasattr(pd.DataFrame, 'map')}")

# Test instance
df = pd.DataFrame({'A': [1,2]})
print("\ndf instance:")
print(f"hasattr(df, 'applymap'): {hasattr(df, 'applymap')}")
print(f"hasattr(df, 'map'): {hasattr(df, 'map')}")
if hasattr(df, 'applymap'):
    print(f"df.applymap is callable: {callable(df.applymap)}")
if hasattr(df, 'map'):
    print(f"df.map is callable: {callable(df.map)}")