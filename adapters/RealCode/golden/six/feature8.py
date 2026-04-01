#!/usr/bin/env python
"""
Feature 8: Exception Re-raising
Reads original error message from stdin, raises it, catches it, wraps it into RuntimeError,
and prints type and final message.
"""

import sys

def main():
    # Read input from stdin
    error_msg = sys.stdin.read().strip()

    try:
        # Raise original exception
        raise ValueError(error_msg)
    except ValueError as e:
        try:
            # Wrap and re-raise
            raise RuntimeError("wrapped: " + str(e))
        except RuntimeError as e2:
            # Print type and message
            print("{}: {}".format(type(e2).__name__, str(e2)))

if __name__ == "__main__":
    main()