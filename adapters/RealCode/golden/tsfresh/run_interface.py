#!/usr/bin/env python
"""
Script for CLI interface testing.
Reads JSON from stdin, outputs results to stdout.
"""

import sys
import json
import tempfile
import os
import subprocess
import pandas as pd


def main():
    # Read JSON from stdin
    input_data = json.load(sys.stdin)

    # Parse input
    command = input_data.get("command")
    input_file_content = input_data.get("input_file")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write input CSV
        input_path = os.path.join(tmpdir, "data.csv")
        with open(input_path, "w") as f:
            f.write(input_file_content)

        # Parse command arguments
        # Extract output filename from command
        args = command.split()
        # Replace --input with actual path
        cmd_args = []
        i = 0
        while i < len(args):
            if args[i] == "--input":
                cmd_args.extend(["--input", input_path])
                i += 2  # Skip original value
            else:
                cmd_args.append(args[i])
                i += 1

        # Run command
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print(f"Command failed: {result.stderr}", file=sys.stderr)
                sys.exit(1)

            # Find output file from command arguments
            output_path = None
            for j, arg in enumerate(cmd_args):
                if arg == "--output" and j + 1 < len(cmd_args):
                    output_path = cmd_args[j + 1]
                    break

            if output_path is None:
                print("No output file specified in command", file=sys.stderr)
                sys.exit(1)

            # Read output CSV
            output_df = pd.read_csv(output_path)

            # Prepare output
            output = {
                "output_file_columns": output_df.columns.tolist(),
                "row_count": len(output_df),
            }

            # Output JSON
            json.dump(output, sys.stdout, indent=2)

        except subprocess.TimeoutExpired:
            print("Command timed out", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()