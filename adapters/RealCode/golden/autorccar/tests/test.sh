#!/bin/bash

# AutoRCCar Test Suite
# This script runs all test cases and outputs results to tests/stdout/

set -e

# Create output directory
mkdir -p tests/stdout

# Clean previous outputs
rm -f tests/stdout/*.txt

# Get list of test case files
test_files=$(find tests/test_cases -name "*.json" | sort)

echo "Running AutoRCCar test suite..."
echo "Found $(echo "$test_files" | wc -l) test case files"

# Function to run a single test case
run_test_case() {
    local test_file="$1"
    local case_index="$2"
    local case_data="$3"
    local output_file="$4"

    # Extract test case details
    local input=$(echo "$case_data" | jq -r '.input')
    local expected_output=$(echo "$case_data" | jq -r '.expected_output')

    # Determine which feature script to run based on filename
    local feature_name=$(basename "$test_file" .json)
    local script_name=""

    case "$feature_name" in
        feature1_video_stream)
            script_name="computer/feature1_video_stream.py"
            ;;
        feature2_nn_training)
            script_name="computer/feature2_nn_training.py"
            ;;
        feature3_1_stop_sign|feature3_2_traffic_light)
            script_name="computer/feature3_object_detection.py"
            ;;
        feature4_distance_calculation)
            script_name="computer/feature4_distance_calculation.py"
            ;;
        feature5_sensor_fusion)
            script_name="computer/feature5_sensor_fusion.py"
            ;;
        feature6_hardware_control)
            script_name="computer/feature6_hardware_control.py"
            ;;
        feature7_data_collection)
            script_name="computer/feature7_data_collection.py"
            ;;
        *)
            echo "Unknown feature: $feature_name"
            return 1
            ;;
    esac

    # Check if script exists
    if [ ! -f "$script_name" ]; then
        echo "Script $script_name not found"
        return 1
    fi

    # Run the script with input
    echo "$input" | python3 "$script_name" > "$output_file" 2>/dev/null
}

# Process each test file
for test_file in $test_files; do
    filename=$(basename "$test_file")
    file_stem="${filename%.json}"

    echo "Processing $filename..."

    # Read test cases from JSON file
    cases_count=$(jq '.cases | length' "$test_file")

    for ((i=0; i<cases_count; i++)); do
        # Extract individual test case
        case_data=$(jq -c ".cases[$i]" "$test_file")

        # Create output filename
        output_file="tests/stdout/${file_stem}@$(printf "%03d" $i).txt"

        # Run test case
        if run_test_case "$test_file" "$i" "$case_data" "$output_file"; then
            echo "  Case $i: $(basename "$output_file")"
        else
            echo "  Case $i: FAILED"
        fi
    done
done

echo "Test suite completed."
echo "Output files saved to tests/stdout/"