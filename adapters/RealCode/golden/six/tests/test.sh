#!/bin/bash
# Test script for Six library
# Runs all test cases and saves outputs to stdout directory

set -e  # Exit on error

# Change to script directory
cd "$(dirname "$0")"

# Run the Python test runner
python3 run_tests.py

echo "Test suite completed successfully"