#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tests.test_runner import load_test_cases, run_feature1_test

def enhance_feature1():
    orig_path = Path('tests/test_cases/feature1_file_discovery.json')
    cases = load_test_cases(orig_path)
    # New cases
    new_cases = []

    # Helper to compute expected output
    def compute_output(input_data):
        return run_feature1_test(input_data)

    # Case 3: empty roots
    input_data = {
        "roots": [],
        "recurse": True
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Case 4: nonexistent root
    input_data = {
        "roots": ["/nonexistent_xyz_123"],
        "recurse": True
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Case 5: search_extensions empty list (no filter)
    input_data = {
        "roots": ["./test_data"],
        "recurse": False,
        "search_extensions": []
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Case 6: search_patterns with wildcard
    input_data = {
        "roots": ["./test_data"],
        "recurse": True,
        "search_patterns": ["*.py"]
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Case 7: filter_include_patterns with ** glob
    input_data = {
        "roots": ["./test_data"],
        "recurse": True,
        "filter_include_patterns": ["src/**"]
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Case 8: overlapping include/exclude
    input_data = {
        "roots": ["./test_data"],
        "recurse": True,
        "filter_include_patterns": ["src/**"],
        "filter_exclude_patterns": ["src/vendor/**"]
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Case 9: ignore_dirs with non-existent dir
    input_data = {
        "roots": ["./test_data"],
        "recurse": True,
        "ignore_dirs": ["dummy"]
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Case 10: multiple roots with one empty
    input_data = {
        "roots": ["./test_data", "/nonexistent_abc"],
        "recurse": False
    }
    new_cases.append({
        "input": input_data,
        "expected_output": compute_output(input_data)
    })

    # Combine original and new cases
    enhanced_cases = cases + new_cases

    # Build enhanced JSON
    enhanced = {
        "description": "FileFinder with extension filtering, ignored directories, and text‑file detection (enhanced with edge cases)",
        "cases": enhanced_cases
    }

    output_path = Path('tests/enhanced_test_cases/feature1_file_discovery.json')
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced, f, indent=4)
    print(f"Enhanced feature1 written to {output_path}")

if __name__ == '__main__':
    enhance_feature1()