#!/usr/bin/env python3
"""
Feature 5: Command Line Interface
Reads input from stdin and prints CLI test results to stdout.
"""

import sys
import json
from cli.main import run_cli_from_input


def main():
    """Main function to handle stdin input and stdout output."""
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Run CLI test
        result = run_cli_from_input(input_data)
        
        # Output result to stdout
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "exit_code": 1,
            "error": f"Invalid JSON input: {str(e)}"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "exit_code": 1,
            "error": f"Unexpected error: {str(e)}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()