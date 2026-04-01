#!/usr/bin/env python
"""
Test runner for Six library features.
Reads test cases from JSON files, runs corresponding feature scripts,
and writes outputs to stdout directory.
"""

import os
import sys
import json
import subprocess

# Map feature names to script paths
FEATURE_SCRIPTS = {
    'feature1_version_detection': '../feature1.py',
    'feature2_type_checking': '../feature2.py',
    'feature3_1_urlparse': '../feature3_1.py',
    'feature3_2_queue': '../feature3_2.py',
    'feature3_3_configparser': '../feature3_3.py',
    'feature4_1_ensure_binary': '../feature4_1.py',
    'feature4_2_ensure_text': '../feature4_2.py',
    'feature5_1_iterkeys': '../feature5_1.py',
    'feature5_2_itervalues': '../feature5_2.py',
    'feature5_3_iteritems': '../feature5_3.py',
    'feature6_metaclass': '../feature6.py',
    'feature7_print': '../feature7.py',
    'feature8_reraise': '../feature8.py',
    'feature9_1_stringio': '../feature9_1.py',
    'feature9_2_bytesio': '../feature9_2.py',
    'feature10_next': '../feature10.py',
}

def run_test(script_path, input_data):
    """Run a feature script with given input and return output."""
    try:
        # Run script with input
        proc = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = proc.communicate(input=input_data)
        # Remove trailing newline
        return stdout.rstrip('\n')
    except Exception as e:
        return f"ERROR: {e}"

def main():
    # Ensure stdout directory exists
    stdout_dir = 'stdout'
    os.makedirs(stdout_dir, exist_ok=True)

    # Find all test case JSON files
    test_cases_dir = 'test_cases'
    if not os.path.exists(test_cases_dir):
        print(f"Test cases directory not found: {test_cases_dir}")
        return 1

    # Process each JSON file
    for filename in os.listdir(test_cases_dir):
        if not filename.endswith('.json'):
            continue

        # Extract feature name without extension
        feature_name = filename[:-5]
        script_path = FEATURE_SCRIPTS.get(feature_name)
        if not script_path:
            print(f"Warning: No script found for {feature_name}")
            continue

        # Read test cases
        json_path = os.path.join(test_cases_dir, filename)
        with open(json_path, 'r') as f:
            try:
                test_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing {json_path}: {e}")
                continue

        # Process each test case
        cases = test_data.get('cases', [])
        for i, case in enumerate(cases):
            input_data = case.get('input', '')
            # Run test
            output = run_test(script_path, input_data)

            # Write output to file
            output_filename = f"{feature_name}@{str(i).zfill(3)}.txt"
            output_path = os.path.join(stdout_dir, output_filename)
            with open(output_path, 'w') as f:
                f.write(output)

            print(f"Processed {feature_name} case {i}")

    print("All tests completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())