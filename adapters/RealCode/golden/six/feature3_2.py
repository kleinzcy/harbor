#!/usr/bin/env python
"""
Feature 3.2: Queue
Reads a string from stdin, puts it into a queue, gets it back, prints it.
"""

import sys
from six import queue_put_get

def main():
    # Read input from stdin
    item = sys.stdin.read().strip()
    result = queue_put_get(item)
    print(result)

if __name__ == "__main__":
    main()