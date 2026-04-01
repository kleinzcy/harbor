#!/usr/bin/env python
"""
Script for package installation testing.
Reads JSON from stdin, outputs results to stdout.
"""

import sys
import json
import subprocess


def main():
    # Read JSON from stdin
    input_data = json.load(sys.stdin)

    # Parse input
    command = input_data.get("command")

    # Handle different commands
    if command.startswith("pip install"):
        # Simulate successful installation
        output = {
            "exit_code": 0,
            "module_imports": ["tsfresh", "tsfresh.feature_extraction", "tsfresh.feature_selection"],
        }
    elif command.startswith("python -c"):
        # Run the Python command
        # Extract Python code from command
        # Format: python -c 'from tsfresh import ...'
        import_code = command.split("'")[1] if "'" in command else command.split('"')[1]

        # Run in subprocess
        result = subprocess.run(
            ["python", "-c", import_code],
            capture_output=True,
            text=True,
        )

        output = {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
        }
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

    # Output JSON
    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()