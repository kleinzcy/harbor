#!/usr/bin/env python
"""
Feature 4.2: Bytes to Text
Reads a bytes literal as string (e.g. b'hello') from stdin, decodes it, prints text.
"""

import sys
from six import ensure_text

def main():
    # Read input from stdin
    input_data = sys.stdin.read().strip()

    # Use ast.literal_eval to safely evaluate the bytes literal
    import ast
    try:
        bytes_obj = ast.literal_eval(input_data)
    except (SyntaxError, ValueError):
        # If evaluation fails, treat as plain string
        bytes_obj = input_data

    # Decode to text
    text = ensure_text(bytes_obj)
    print(text)

if __name__ == "__main__":
    main()