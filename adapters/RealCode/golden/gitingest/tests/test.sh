#!/bin/bash
# GitIngest Test Suite
# Run all test cases and output results to stdout/{filename.stem}@{case_index.zfill(3)}.txt

set -e  # Exit on error

# Change to tests directory first
cd "$(dirname "$0")"

# Setup test environment first
echo "Setting up test environment..." >&2
./setup_test_env.sh >&2

# Clean up previous test directories
echo "Cleaning up previous test directories..." >&2
rm -rf /tmp/test-repo-1 /tmp/test-repo-2 /tmp/test-repo-3 /tmp/test-repo-4 /tmp/test-repo-5 /tmp/test-repo-6 /tmp/test-repo-7 /tmp/test-repo-8 /tmp/test-scan /tmp/test-filter /tmp/test-size /tmp/test-nonexistent /tmp/test-empty /tmp/test-nested /tmp/test-ignore-dir /tmp/test-binary /tmp/test-exact-size /tmp/test-hidden 2>/dev/null || true

# Create output directories
mkdir -p output
mkdir -p stdout

# Clean up previous stdout outputs
rm -rf stdout/* 2>/dev/null || true
rm -f stdout.txt 2>/dev/null || true

echo "Starting GitIngest test suite..." >&2

# Function to run a test case
run_test() {
    local feature_name="$1"
    local test_file="$2"
    local script_name="$3"

    echo "Running $feature_name..." >&2

    # Get filename stem (without .json extension)
    local stem=$(basename "$test_file" .json)

    # Read test cases
    test_cases=$(cat "$test_file" | jq -c '.cases[]')

    # Initialize case index
    local case_index=0

    # Run each test case
    while IFS= read -r test_case; do
        input=$(echo "$test_case" | jq -c '.input')

        # Generate padded index (000, 001, etc.)
        local padded_index=$(printf "%03d" "$case_index")

        # Define output file
        local output_file="stdout/${stem}@${padded_index}.txt"

        # Run the test script with input and write to output file
        python3 "../gitingest/$script_name" <<< "$input" > "$output_file"

        # Increment case index
        case_index=$((case_index + 1))
    done <<< "$test_cases"
}

# Run all feature tests
run_test "Feature 1: Repository Cloning" "test_cases/feature1_repository_cloning.json" "feature1_clone.py"
run_test "Feature 2: File System Scanning" "test_cases/feature2_file_scanning.json" "feature2_scan.py"
run_test "Feature 3: Jupyter Notebook Processing" "test_cases/feature3_notebook_processing.json" "feature3_notebook.py"
run_test "Feature 4: Web API Interface" "test_cases/feature4_web_api.json" "feature4_api.py"
run_test "Feature 5: Command Line Interface" "test_cases/feature5_cli_interface.json" "feature5_cli.py"
run_test "Feature 6.1: Python Code Analysis" "test_cases/feature6_1_python_analysis.json" "feature6_1_python.py"
run_test "Feature 6.2: Configuration File Parsing" "test_cases/feature6_2_config_parsing.json" "feature6_2_config.py"

echo "Test suite completed." >&2