#!/usr/bin/env python
"""
Feature 2: Type Checking
Reads a value from stdin, prints classification: string, integer, or other.
"""

import sys
from six import classify_type

def main():
    # Read input from stdin
    input_data = sys.stdin.read().strip()

    # Parse input
    value = None
    # Try to convert to integer
    try:
        value = int(input_data)
    except ValueError:
        # Try to convert to float
        try:
            value = float(input_data)
        except ValueError:
            # Otherwise treat as string
            value = input_data

    # Classify and print
    print(classify_type(value))

if __name__ == "__main__":
    main()