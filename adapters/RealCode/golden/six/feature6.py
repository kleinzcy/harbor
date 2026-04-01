#!/usr/bin/env python
"""
Feature 6: Metaclass Compatibility
Reads a class name from stdin, creates that class using a custom metaclass that injects injected=True attribute,
prints whether the attribute exists.
"""

import sys
from six import create_class_with_metaclass

# Define metaclass that injects attribute
class InjectionMetaclass(type):
    def __new__(cls, name, bases, dct):
        dct['injected'] = True
        return super(InjectionMetaclass, cls).__new__(cls, name, bases, dct)

def main():
    # Read input from stdin
    class_name = sys.stdin.read().strip()
    if not class_name:
        return

    # Create class with metaclass
    MyClass = create_class_with_metaclass(InjectionMetaclass, class_name, (), {})

    # Check if attribute exists
    result = getattr(MyClass, 'injected', False)
    print(result)

if __name__ == "__main__":
    main()