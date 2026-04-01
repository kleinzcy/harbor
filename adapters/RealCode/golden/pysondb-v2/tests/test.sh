#!/bin/bash

# Test runner for pysonDB-v2
# Executes all test cases and saves outputs to tests/stdout/

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_TEST_RUNNER="$SCRIPT_DIR/run_tests.py"

echo "Starting pysonDB-v2 test suite..."
echo

# Check if Python test runner exists
if [ ! -f "$PYTHON_TEST_RUNNER" ]; then
    echo "Error: Test runner not found at $PYTHON_TEST_RUNNER"
    exit 1
fi

# Run the Python test runner
python3 "$PYTHON_TEST_RUNNER"

exit_code=$?
echo
if [ $exit_code -eq 0 ]; then
    echo "Test suite completed successfully."
else
    echo "Test suite failed with exit code $exit_code."
fi

exit $exit_code