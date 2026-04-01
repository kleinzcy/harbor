"""
Lazy collection classes for pytz.
"""


class LazyList:
    """A list that defers computation until first access."""
    
    def __init__(self, fill_func):
        self._fill_func = fill_func
        self._data = None
        self._filled = False
    
    def _ensure_filled(self):
        if not self._filled:
            self._data = self._fill_func()
            self._filled = True
    
    def __len__(self):
        self._ensure_filled()
        return len(self._data)
    
    def __getitem__(self, index):
        self._ensure_filled()
        return self._data[index]
    
    def __iter__(self):
        self._ensure_filled()
        return iter(self._data)
    
    def __contains__(self, item):
        self._ensure_filled()
        return item in self._data
    
    def __repr__(self):
        if self._filled:
            return repr(self._data)
        return "<LazyList unfilled>"
    
    def __str__(self):
        if self._filled:
            return str(self._data)
        return "<LazyList unfilled>"
    
    def index(self, value, start=0, stop=None):
        self._ensure_filled()
        if stop is None:
            return self._data.index(value, start)
        return self._data.index(value, start, stop)
    
    def count(self, value):
        self._ensure_filled()
        return self._data.count(value)


class LazySet:
    """A set that defers computation until first access."""
    
    def __init__(self, fill_func):
        self._fill_func = fill_func
        self._data = None
        self._filled = False
    
    def _ensure_filled(self):
        if not self._filled:
            self._data = self._fill_func()
            self._filled = True
    
    def __len__(self):
        self._ensure_filled()
        return len(self._data)
    
    def __iter__(self):
        self._ensure_filled()
        return iter(self._data)
    
    def __contains__(self, item):
        self._ensure_filled()
        return item in self._data
    
    def __repr__(self):
        if self._filled:
            return repr(self._data)
        return "<LazySet unfilled>"
    
    def __str__(self):
        if self._filled:
            return str(self._data)
        return "<LazySet unfilled>"
    
    def union(self, other):
        self._ensure_filled()
        return self._data.union(other)
    
    def intersection(self, other):
        self._ensure_filled()
        return self._data.intersection(other)
    
    def difference(self, other):
        self._ensure_filled()
        return self._data.difference(other)
    
    def symmetric_difference(self, other):
        self._ensure_filled()
        return self._data.symmetric_difference(other)
    
    def issubset(self, other):
        self._ensure_filled()
        return self._data.issubset(other)
    
    def issuperset(self, other):
        self._ensure_filled()
        return self._data.issuperset(other)


class LazyDict:
    """A dictionary that defers computation until first access."""
    
    def __init__(self, fill_func):
        self._fill_func = fill_func
        self._data = None
        self._filled = False
    
    def _ensure_filled(self):
        if not self._filled:
            self._data = self._fill_func()
            self._filled = True
    
    def __len__(self):
        self._ensure_filled()
        return len(self._data)
    
    def __getitem__(self, key):
        self._ensure_filled()
        return self._data[key]
    
    def __iter__(self):
        self._ensure_filled()
        return iter(self._data)
    
    def __contains__(self, key):
        self._ensure_filled()
        return key in self._data
    
    def __repr__(self):
        if self._filled:
            return repr(self._data)
        return "<LazyDict unfilled>"
    
    def __str__(self):
        if self._filled:
            return str(self._data)
        return "<LazyDict unfilled>"
    
    def get(self, key, default=None):
        self._ensure_filled()
        return self._data.get(key, default)
    
    def keys(self):
        self._ensure_filled()
        return self._data.keys()
    
    def values(self):
        self._ensure_filled()
        return self._data.values()
    
    def items(self):
        self._ensure_filled()
        return self._data.items()