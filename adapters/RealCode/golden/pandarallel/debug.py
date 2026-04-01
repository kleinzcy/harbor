import pandas as pd
print('pandas version:', pd.__version__)
df = pd.DataFrame({'A': [1, 2]})
print('has applymap:', hasattr(df, 'applymap'))
print('has map:', hasattr(df, 'map'))
if hasattr(df, 'map'):
    print('map callable:', callable(df.map))
    try:
        df.map(lambda x: x)
        print('map works with lambda')
    except Exception as e:
        print('map error:', e)
if hasattr(df, 'applymap'):
    print('applymap callable:', callable(df.applymap))
    try:
        df.applymap(lambda x: x)
        print('applymap works')
    except Exception as e:
        print('applymap error:', e)