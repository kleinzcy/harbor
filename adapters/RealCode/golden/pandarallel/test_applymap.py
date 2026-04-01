import sys
sys.path.insert(0, '.')
from pandarallel.utils import get_dataframe_applymap_name, dataframe_applymap
import pandas as pd

print('pandas version:', pd.__version__)
print('method name:', get_dataframe_applymap_name())

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print('df:', df)
try:
    result = dataframe_applymap(df, lambda x: x*2)
    print('dataframe_applymap succeeded:', result)
except Exception as e:
    print('dataframe_applymap failed:', e)
    import traceback
    traceback.print_exc()

# Now test parallel_applymap
from pandarallel import initialize
initialize()
try:
    result = df.parallel_applymap(lambda x: x*2)
    print('parallel_applymap succeeded:', result)
except Exception as e:
    print('parallel_applymap failed:', e)
    traceback.print_exc()