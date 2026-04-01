#!/bin/bash
# Test script for jusText library

set -e

# Change to script directory to ensure relative paths work
cd "$(dirname "$0")"

# Create output directory
mkdir -p enhanced_output

# Function to run a test case
run_test() {
    local test_file="$1"
    local test_name="$2"
    local input="$3"
    local expected="$4"
    
    echo "Running test: $test_name"
    
    # Run the extraction
    echo "$input" | python3 ../extract_text.py > "enhanced_output/${test_name}.txt" 2>/dev/null
    
    # Get actual output
    actual=$(cat "enhanced_output/${test_name}.txt")
    
    # Compare with expected
    if [ "$actual" = "$expected" ]; then
        echo "PASS"
    else
        echo "FAIL"
        echo "Expected: $expected"
        echo "Actual: $actual"
    fi
}

# Function to run JSON test cases
run_json_tests() {
    local json_file="$1"
    local feature_name="$2"
    
    echo "=== Testing $feature_name ==="
    
    # Parse JSON and run each test case
    python3 -c "
import json
import sys
import subprocess
import os

with open('$json_file', 'r') as f:
    data = json.load(f)

for i, case in enumerate(data['cases']):
    input_html = case['input']
    expected_output = case['expected_output']
    
    # Run extraction
    result = subprocess.run(
        ['python3', '../extract_text.py'],
        input=input_html,
        capture_output=True,
        text=True
    )
    
    actual_output = result.stdout.strip()
    
    # Print only the output (no test names or status)
    print(actual_output)
" > "enhanced_output/${feature_name}_output.txt"
}

# Run all feature tests
echo "Starting jusText test suite..."

# Feature 1: Basic extraction
run_json_tests "enhanced_test_cases/feature1_basic_extraction.json" "feature1"

# Feature 2: Boilerplate detection
run_json_tests "enhanced_test_cases/feature2_boilerplate_detection.json" "feature2"

# Feature 3: Encoding handling
run_json_tests "enhanced_test_cases/feature3_encoding_handling.json" "feature3"

# Feature 4: Multilingual support (special handling)
echo "=== Testing multilingual support ==="
python3 -c "
import json
import sys
sys.path.insert(0, '..')
from justext import load_stoplist

with open('enhanced_test_cases/feature4_multilingual_support.json', 'r') as f:
    data = json.load(f)

for case in data['cases']:
    language = case['input']
    expected = json.loads(case['expected_output'])

    try:
        stopwords = load_stoplist(language.lower())
        # Take first 10 stopwords for comparison
        actual = list(stopwords)[:10]

        # Print as JSON string
        import json
        print(json.dumps(actual, ensure_ascii=False))
    except Exception as e:
        print(f'Error: {e}')
" > "enhanced_output/feature4_output.txt"

# Feature 5: HTML preprocessing
run_json_tests "enhanced_test_cases/feature5_html_preprocessing.json" "feature5"

# Feature 6: Context classification
run_json_tests "enhanced_test_cases/feature6_context_classification.json" "feature6"

# Feature 7: Link density
run_json_tests "enhanced_test_cases/feature7_link_density.json" "feature7"

# Combine all outputs into enhanced_stdout.txt
echo "Combining all test outputs..."
cat enhanced_output/*_output.txt > enhanced_stdout.txt

echo "Test suite completed. Output saved to enhanced_stdout.txt"