#!/usr/bin/env python
"""
Feature 3.1: URL Parsing
Reads a URL from stdin, prints the protocol scheme.
"""

import sys
from six import get_url_scheme

def main():
    # Read input from stdin
    url = sys.stdin.read().strip()
    print(get_url_scheme(url))

if __name__ == "__main__":
    main()