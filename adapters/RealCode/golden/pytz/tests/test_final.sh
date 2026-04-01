#!/bin/bash
# pytz final test suite entry point
# Execute all tests using final test cases and redirect output to stdout.txt
# Only output test results, no extra logs

set -e  # Exit on error

# Enter script directory
cd "$(dirname "$0")"

# Clear previous output file
> stdout.txt

# Run final test runner
python run_final_tests.py >> stdout.txt 2>&1

echo "Test output saved to stdout.txt"