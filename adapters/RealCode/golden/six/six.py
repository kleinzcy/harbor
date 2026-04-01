"""
Six - Python 2/3 Compatibility Library
A lightweight library for writing code that runs on both Python 2.7 and Python 3.3+
"""

import sys

# Feature 1: Version Detection
def python_version():
    """Return 'Python 2' or 'Python 3'"""
    if sys.version_info[0] == 2:
        return "Python 2"
    else:
        return "Python 3"

# Feature 2: Type Checking
def is_string(value):
    """Check if value is a string (str or unicode)"""
    if sys.version_info[0] == 2:
        return isinstance(value, basestring)
    else:
        return isinstance(value, str)

# Workaround for Python 3 where basestring doesn't exist
if sys.version_info[0] == 3:
    basestring = str

def is_integer(value):
    """Check if value is an integer (int or long)"""
    if sys.version_info[0] == 2:
        # Python 2 has int and long
        return isinstance(value, (int, long))
    else:
        # Python 3 only has int (long is just int)
        return isinstance(value, int)

# Workaround for Python 3 where long doesn't exist
if sys.version_info[0] == 3:
    long = int

def classify_type(value):
    """Classify value as 'string', 'integer', or 'other'"""
    if is_string(value):
        return "string"
    elif is_integer(value):
        return "integer"
    else:
        return "other"

# Feature 3: Standard Library Compatibility
# 3.1 URL Parsing
try:
    from urlparse import urlparse  # Python 2
except ImportError:
    from urllib.parse import urlparse  # Python 3

def get_url_scheme(url):
    """Extract scheme from URL"""
    return urlparse(url).scheme

# 3.2 Queue
try:
    from Queue import Queue  # Python 2
except ImportError:
    from queue import Queue  # Python 3

def queue_put_get(item):
    """Put item into queue and get it back"""
    q = Queue()
    q.put(item)
    return q.get()

# 3.3 Config Parser
try:
    from ConfigParser import ConfigParser  # Python 2
except ImportError:
    from configparser import ConfigParser  # Python 3

def create_config():
    """Create a config with server section"""
    if sys.version_info[0] == 2:
        config = ConfigParser()
    else:
        config = ConfigParser()
    config.add_section('server')
    config.set('server', 'host', 'localhost')
    config.set('server', 'port', '8080')
    return config

def get_config_value(config, section, key):
    """Get value from config"""
    return config.get(section, key)

# Feature 4: String and Bytes Conversion
def ensure_binary(text, encoding='utf-8'):
    """Convert text to bytes"""
    if sys.version_info[0] == 2:
        if isinstance(text, unicode):
            return text.encode(encoding)
        else:
            return text
    else:
        if isinstance(text, str):
            return text.encode(encoding)
        else:
            return text

def ensure_text(data, encoding='utf-8'):
    """Convert bytes to text"""
    if sys.version_info[0] == 2:
        if isinstance(data, str):
            return data.decode(encoding)
        else:
            return data
    else:
        if isinstance(data, bytes):
            return data.decode(encoding)
        else:
            return data

# Feature 5: Dictionary Iteration
def iterkeys(d):
    """Iterate over dictionary keys (memory-efficient)"""
    return d.iterkeys() if sys.version_info[0] == 2 else d.keys()

def itervalues(d):
    """Iterate over dictionary values (memory-efficient)"""
    return d.itervalues() if sys.version_info[0] == 2 else d.values()

def iteritems(d):
    """Iterate over dictionary items (memory-efficient)"""
    return d.iteritems() if sys.version_info[0] == 2 else d.items()

# Feature 6: Metaclass Compatibility
def with_metaclass(meta, *bases):
    """Create a class with a metaclass compatible with Python 2 and 3"""
    # This is based on six.with_metaclass
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})

# Alternative: function to create class with metaclass
def create_class_with_metaclass(meta, name, bases=None, dct=None):
    """Create a class with given metaclass"""
    if bases is None:
        bases = ()
    if dct is None:
        dct = {}
    if sys.version_info[0] == 2:
        # Python 2: metaclass argument not supported in type()
        # Use __metaclass__ in class dictionary
        dct['__metaclass__'] = meta
        return type(name, bases, dct)
    else:
        # Python 3: use metaclass keyword argument
        return meta(name, bases, dct)

# Feature 7: Print Function
def print_function(*args, **kwargs):
    """Print function compatible with both Python 2 and 3"""
    # In Python 2, print is a statement, but we can use __future__ import
    # This function should be used with from __future__ import print_function
    # For simplicity, we'll just use the built-in print
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    sys.stdout.write(sep.join(str(arg) for arg in args) + end)

# Feature 8: Exception Re-raising
def reraise(exc_type, exc_value, exc_traceback=None):
    """Re-raise exception preserving traceback"""
    if exc_traceback is None:
        exc_traceback = sys.exc_info()[2]
    # This is based on six.reraise
    if exc_value is None:
        exc_value = exc_type()
    if exc_value.__traceback__ is not exc_traceback:
        raise exc_value.with_traceback(exc_traceback)
    raise exc_value

# Feature 9: In-memory String and Bytes Buffers
try:
    from cStringIO import StringIO  # Python 2 fast version
except ImportError:
    from io import StringIO  # Python 3

try:
    from io import BytesIO  # Python 2.6+ and Python 3
except ImportError:
    from cStringIO import StringIO as BytesIO  # Fallback

def text_buffer_write_read(text):
    """Write text to buffer and read it back"""
    buffer = StringIO()
    buffer.write(text)
    buffer.seek(0)
    return buffer.read()

def bytes_buffer_write_read(data):
    """Write bytes to buffer and read it back"""
    buffer = BytesIO()
    if sys.version_info[0] == 2 and isinstance(data, unicode):
        data = data.encode('utf-8')
    buffer.write(data)
    buffer.seek(0)
    return buffer.read()

# Feature 10: Iterator Advancement
def next_item(iterator):
    """Get next item from iterator"""
    return next(iterator)

def advance_iterator(iterator, n):
    """Advance iterator n times, yield results"""
    for _ in range(n):
        try:
            yield next(iterator)
        except StopIteration:
            yield "StopIteration"
            break