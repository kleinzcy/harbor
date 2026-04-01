#!/usr/bin/env python
"""
Feature 3.3: Config Parser
Reads section and key from stdin (separated by space), prints value from built-in config.
"""

import sys
from six import create_config, get_config_value

def main():
    # Read input from stdin
    input_data = sys.stdin.read().strip()
    if not input_data:
        return

    # Parse section and key
    parts = input_data.split()
    if len(parts) != 2:
        return

    section, key = parts[0], parts[1]

    # Create config (built-in with server section)
    config = create_config()

    # Get value and print
    value = get_config_value(config, section, key)
    print(value)

if __name__ == "__main__":
    main()