#!/usr/bin/env python
"""
Feature 5.2: Iterate Values
Reads dictionary as comma-separated key:value pairs, prints all values sorted by their key alphabetically, one per line.
"""

import sys
from six import iterkeys

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

    # Iterate values sorted by key
    for key in sorted(iterkeys(d)):
        print(d[key])

if __name__ == "__main__":
    main()