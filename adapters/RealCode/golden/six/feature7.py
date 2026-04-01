#!/usr/bin/env python
"""
Feature 7: Print Function
Reads space-separated words from stdin, prints them joined by a single space.
Uses print as a function with keyword arguments.
"""

from __future__ import print_function
import sys

def main():
    # Read input from stdin
    input_data = sys.stdin.read().strip()
    # Split by spaces
    words = input_data.split()
    # Print joined by single space using print function
    print(*words, sep=' ')

if __name__ == "__main__":
    main()