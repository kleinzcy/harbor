import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pytz

# Test feature2 lazy collections
print('Testing LazyList:')
lst = pytz.LazyList([1, 2, 3])
print('Length:', len(lst))
print('Contains 2:', 2 in lst)
print('Index 1:', lst[1])
print('Iteration:', list(lst))

print('\nTesting LazySet:')
st = pytz.LazySet([1, 2, 3])
print('Length:', len(st))
print('Contains 2:', 2 in st)
print('Iteration:', list(st))

print('\nTesting LazyDict:')
dct = pytz.LazyDict({'x': 1, 'y': 2})
print('Length:', len(dct))
print('Contains x:', 'x' in dct)
print('Get y:', dct.get('y'))
print('Iteration keys:', list(dct))

# Test some specific operations
print('\n--- Additional tests ---')
print('LazyList repr:', repr(lst))
print('LazySet repr:', repr(st))
print('LazyDict repr:', repr(dct))

# Test empty collections
print('\nEmpty LazyList:', list(pytz.LazyList([])))
print('Empty LazySet:', list(pytz.LazySet([])))
print('Empty LazyDict:', list(pytz.LazyDict({})))