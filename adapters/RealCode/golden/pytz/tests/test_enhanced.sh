#!/bin/bash
# pytz enhanced test suite entry点
# Execute all tests using enhanced test cases and redirect output to stdout.txt
# Only output test results, no extra logs

set -e  # Exit on error

# Enter script directory
cd "$(dirname "$0")"

# Clear previous output file
> stdout.txt

# Run silent test runner with enhanced test cases
python run_enhanced_tests.py >> stdout.txt 2>&1

echo "Test output saved to stdout.txt"