#!/usr/bin/env python
"""
Feature 1: Version Detection
Reads from stdin (no input required), prints Python version label.
"""

from six import python_version

def main():
    # No input needed, just detect and print version
    print(python_version())

if __name__ == "__main__":
    main()