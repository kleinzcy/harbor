#!/bin/bash
# Entry point for unittest-parametrize test suite

set -e

# Change to script directory
cd "$(dirname "$0")"

# Create output directory
mkdir -p stdout

# Run test runner
python test_runner.py "$@"

echo "Test execution completed. Output files written to tests/stdout/"