#!/usr/bin/env python
"""
Feature 9.1: Text Buffer
Reads a text string from stdin, writes to in-memory text buffer, reads back, prints it.
"""

import sys
from six import text_buffer_write_read

def main():
    # Read input from stdin
    text = sys.stdin.read().strip()
    result = text_buffer_write_read(text)
    print(result)

if __name__ == "__main__":
    main()