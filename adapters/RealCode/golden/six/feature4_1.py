#!/usr/bin/env python
"""
Feature 4.1: Text to Bytes
Reads a plain text string from stdin, converts to bytes, prints bytes representation.
"""

import sys
from six import ensure_binary

def main():
    # Read input from stdin
    text = sys.stdin.read().strip()
    # Convert to bytes
    bytes_data = ensure_binary(text)
    # Print bytes representation like Python 3
    # In Python 2, repr of bytes is just '...', not b'...'
    # We need to output b'...' format
    if isinstance(bytes_data, str):
        # Python 2: bytes is str
        print("b'{}'".format(bytes_data))
    else:
        # Python 3: bytes is bytes
        print(repr(bytes_data))

if __name__ == "__main__":
    main()