#!/usr/bin/env python3
"""
Run all test cases and generate individual output files in stdout/ directory.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from justext import extract_text, load_stoplist


def run_feature_test(test_file: Path, stdout_dir: Path) -> list:
    """Run tests from a JSON test file and write individual output files."""
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    outputs = []
    stem = test_file.stem  # e.g., "feature1_basic_extraction"

    for i, case in enumerate(data['cases']):
        input_data = case['input']
        expected = case['expected_output']

        # Special handling for multilingual support test
        if 'multilingual' in str(test_file):
            try:
                stopwords = load_stoplist(input_data.lower())
                # Take first 10 stopwords
                actual = list(stopwords)[:10]
                output = json.dumps(actual, ensure_ascii=False)
            except Exception as e:
                output = f"Error: {e}"
        else:
            # Normal HTML extraction test
            paragraphs = extract_text(input_data)
            content_paragraphs = [p.text for p in paragraphs if not p.is_boilerplate]
            output = "\n".join(content_paragraphs)

        outputs.append(output)

        # Write individual output file
        case_index = str(i).zfill(3)  # 3-digit zero-padded index
        output_filename = f"{stem}@{case_index}.txt"
        output_path = stdout_dir / output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

    return outputs


def main():
    """Run all test cases."""
    test_dir = Path(__file__).parent / "test_cases"
    stdout_dir = Path(__file__).parent / "stdout"

    # Create stdout directory if it doesn't exist
    stdout_dir.mkdir(exist_ok=True)

    # Run tests for each feature
    test_files = sorted(test_dir.glob("feature*.json"))

    for test_file in test_files:
        print(f"Processing {test_file.name}...")
        run_feature_test(test_file, stdout_dir)

    print(f"All test outputs written to {stdout_dir}/")


if __name__ == "__main__":
    main()