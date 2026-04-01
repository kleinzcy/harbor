#!/bin/bash
set -e

# Ensure stdout directory exists
mkdir -p tests/stdout

# Run the test suite
echo "Starting test suite execution..."
python3 tests/run_tests.py 2>&1 | tee tests/test.log

# Check exit status
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Test execution failed. See tests/test.log for details."
    exit 1
fi

echo "All test outputs written to tests/stdout/"