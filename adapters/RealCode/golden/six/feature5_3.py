#!/usr/bin/env python
"""
Feature 5.3: Iterate Items
Reads dictionary as comma-separated key:value pairs, prints all key-value pairs sorted by key, formatted as key=value, one per line.
"""

import sys
from six import iteritems

def main():
    # Read input from stdin
    input_data = sys.stdin.read().strip()
    if not input_data:
        return

    # Parse dictionary
    d = {}
    pairs = input_data.split(',')
    for pair in pairs:
        if ':' not in pair:
            continue
        key, value = pair.split(':', 1)
        # Try to convert value to int
        try:
            value = int(value)
        except ValueError:
            pass
        d[key.strip()] = value

    # Iterate items sorted by key
    for key, value in sorted(iteritems(d)):
        print("{}={}".format(key, value))

if __name__ == "__main__":
    main()