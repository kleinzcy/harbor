#!/usr/bin/env python3
"""
Feature 2: File System Scanning
Reads input from stdin and prints scanning results to stdout.
"""

import sys
import json
from core.scanner import scan_directory_from_input


def main():
    """Main function to handle stdin input and stdout output."""
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Scan directory
        result = scan_directory_from_input(input_data)
        
        # Output result to stdout
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON input: {str(e)}"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()