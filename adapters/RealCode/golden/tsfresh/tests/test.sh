#!/bin/bash
# Test runner for tsfresh

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running tsfresh test suite..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found" >&2
    exit 1
fi

# Run the Python test runner
python3 run_tests.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Test suite completed successfully"
    exit 0
else
    echo "Test suite failed" >&2
    exit 1
fi