#!/usr/bin/env python
"""
Feature 10: Iterator Advancement
Reads comma-separated list of integers and a count n separated by space,
advances iterator n times, prints each value on separate line.
If iterator exhausted, prints StopIteration.
"""

import sys
from six import advance_iterator

def main():
    # Read input from stdin
    input_data = sys.stdin.read().strip()
    if not input_data:
        return

    # Split by space: first part is list, second is count
    parts = input_data.split()
    if len(parts) != 2:
        return

    list_str, n_str = parts[0], parts[1]

    # Parse list
    try:
        numbers = [int(x) for x in list_str.split(',')]
    except ValueError:
        return

    # Parse n
    try:
        n = int(n_str)
    except ValueError:
        return

    # Create iterator
    iterator = iter(numbers)

    # Advance and print results
    for value in advance_iterator(iterator, n):
        print(value)

if __name__ == "__main__":
    main()