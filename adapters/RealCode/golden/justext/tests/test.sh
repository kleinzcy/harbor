#!/bin/bash
# Test script for jusText library
# Runs the full test suite and writes individual test case outputs to tests/stdout/

set -e

# Change to script directory to ensure relative paths work
cd "$(dirname "$0")"

echo "Starting jusText test suite..."

# Run the Python test runner which handles all test cases
python3 run_tests.py

echo "Test suite completed. Output files written to stdout/"