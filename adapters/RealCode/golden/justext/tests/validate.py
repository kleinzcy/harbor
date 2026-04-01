#!/usr/bin/env python3
import json
import subprocess
import sys
import os

def run_extract(html):
    """Run extract_text.py with given HTML input."""
    result = subprocess.run(
        ['python3', '../extract_text.py'],
        input=html,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def validate_feature(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    print(f"Validating {json_file} ({len(data['cases'])} cases)")
    all_pass = True
    for i, case in enumerate(data['cases']):
        input_html = case['input']
        expected = case['expected_output']
        actual = run_extract(input_html)
        if actual == expected:
            print(f"  Case {i+1}: PASS")
        else:
            print(f"  Case {i+1}: FAIL")
            print(f"    Input: {input_html[:50]}...")
            print(f"    Expected: {repr(expected)}")
            print(f"    Actual:   {repr(actual)}")
            all_pass = False
    return all_pass

def main():
    enhanced_dir = 'enhanced_test_cases'
    json_files = [
        'feature1_basic_extraction.json',
        'feature2_boilerplate_detection.json',
        'feature3_encoding_handling.json',
        'feature5_html_preprocessing.json',
        'feature6_context_classification.json',
        'feature7_link_density.json',
    ]
    # feature4 is special (stoplist), skip for now
    all_ok = True
    for fname in json_files:
        path = os.path.join(enhanced_dir, fname)
        if not validate_feature(path):
            all_ok = False
    if all_ok:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()