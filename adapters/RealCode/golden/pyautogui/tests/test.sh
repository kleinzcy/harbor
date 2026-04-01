#!/bin/bash
# Main test entry point for PyAutoGUI test suite
# Runs all test cases and outputs results to tests/stdout/

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create output directory if it doesn't exist
mkdir -p stdout

# Function to run a single test case
run_test_case() {
    local json_file="$1"
    local case_index="$2"
    local input_json="$3"
    local output_file

    # Generate output filename: {filename.stem}@{case_index.zfill(3)}.txt
    local base_name=$(basename "$json_file" .json)
    output_file="stdout/${base_name}@$(printf "%03d" "$case_index").txt"

    # Run test_runner.py with input JSON, capture output
    echo "$input_json" | python3 test_runner.py > "$output_file" 2>&1

    # Check if test_runner.py exited with error
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        # If there was an error, ensure output file contains error info
        echo "Test case $case_index failed with exit code $exit_code" >> "$output_file"
    fi

    echo "  Generated: $output_file"
}

# Process each JSON test case file
for json_file in test_cases/*.json; do
    if [ ! -f "$json_file" ]; then
        continue
    fi

    echo "Processing: $(basename "$json_file")"

    # Parse JSON file to extract individual test cases
    # Use Python to parse JSON and output each case as separate JSON
    python3 -c "
import json
import sys

with open('$json_file', 'r') as f:
    data = json.load(f)

cases = data.get('cases', [])
for i, case in enumerate(cases):
    input_data = case.get('input', {})
    print(json.dumps(input_data))
" | while IFS= read -r line; do
        # Get case index (0-based)
        case_index=$((case_index + 1))

        # Run test case with the input JSON
        run_test_case "$json_file" "$case_index" "$line"
    done

    # Reset case index for next file
    case_index=0
done

echo "All tests completed. Output files are in tests/stdout/"