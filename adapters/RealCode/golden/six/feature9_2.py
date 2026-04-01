#!/usr/bin/env python
"""
Feature 9.2: Binary Buffer
Reads a plain ASCII string from stdin, encodes to bytes, writes to binary buffer, reads back, decodes, prints.
"""

import sys
from six import bytes_buffer_write_read, ensure_binary, ensure_text

def main():
    # Read input from stdin
    text = sys.stdin.read().strip()
    # Encode to bytes
    bytes_data = ensure_binary(text)
    # Write to buffer and read back
    result_bytes = bytes_buffer_write_read(bytes_data)
    # Decode to text
    result_text = ensure_text(result_bytes)
    print(result_text)

if __name__ == "__main__":
    main()