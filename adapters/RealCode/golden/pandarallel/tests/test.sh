#!/bin/bash
# Test runner script for Pandarallel

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Pandarallel Test Suite ==="
echo "Starting at: $(date)"
echo

# Create output directory
mkdir -p stdout

# Install dependencies if needed
echo "Checking dependencies..."
python -c "import pandas" 2>/dev/null || {
    echo "pandas not found. Installing..."
    pip install pandas
}

python -c "import psutil" 2>/dev/null || {
    echo "psutil not found. Installing..."
    pip install psutil
}

python -c "import tqdm" 2>/dev/null || {
    echo "tqdm not found. Installing..."
    pip install tqdm
}

python -c "import dill" 2>/dev/null || {
    echo "dill not found. Installing..."
    pip install dill
}

echo "Dependencies OK"
echo

# Run the test runner
echo "Running test cases..."
python test_runner.py

echo
echo "=== Test Suite Complete ==="
echo "Finished at: $(date)"
echo

# Show summary
echo "Output files in stdout/:"
ls -la stdout/ | head -20

echo
echo "First few output files:"
for f in stdout/*.txt; do
    if [ -f "$f" ]; then
        echo "  $(basename "$f"): $(head -c 50 "$f" | tr '\n' ' ')..."
    fi
done