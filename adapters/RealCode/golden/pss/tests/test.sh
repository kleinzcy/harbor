#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Running PSS test suite..."

# Create stdout directory if it doesn't exist
mkdir -p stdout

# Run the test runner
python3 test_runner.py

echo "All test outputs written to tests/stdout/"