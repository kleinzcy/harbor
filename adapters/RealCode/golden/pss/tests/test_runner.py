#!/usr/bin/env python3
"""
Test runner for PSS.

Reads JSON test cases from tests/test_cases/, executes the appropriate
function, and writes output to tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt
"""
import ast
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union

# Add parent directory to path to import pss module
sys.path.insert(0, str(Path(__file__).parent.parent))

from pss import filefinder, matcher, formatter, cli, utils


def decode_bytes_literal(s: str) -> bytes:
    """
    Convert a string representing a Python bytes literal (b'...' or b"...") to bytes.

    The string may have been processed by JSON decoding, which interprets
    escape sequences like \n as newline characters.
    """
    if not (s.startswith("b'") or s.startswith('b"')):
        raise ValueError(f"Not a bytes literal: {s!r}")

    # Find the opening quote character (same as the one after 'b')
    quote_char = s[1]  # either ' or "

    # Find the matching closing quote (simple: last character should be the same quote)
    if s[-1] != quote_char:
        raise ValueError(f"Mismatched quotes: {s!r}")

    # Extract content between quotes
    content = s[2:-1]

    # Encode as bytes using latin-1 (preserves all code points 0-255)
    return content.encode('latin-1')


def eval_bytes_literals(obj: Any) -> Any:
    """
    Recursively convert strings that look like Python bytes literals (b'...')
    into actual bytes objects.

    This handles the special format used in test case JSON files.
    """
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, str):
        # Check if string starts with b' or b"
        if obj.startswith("b'") or obj.startswith('b"'):
            try:
                return decode_bytes_literal(obj)
            except (SyntaxError, ValueError):
                # If literal_eval fails, return the string as-is
                return obj
        return obj
    elif isinstance(obj, dict):
        return {k: eval_bytes_literals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [eval_bytes_literals(item) for item in obj]
    else:
        return obj


def load_test_cases(json_path: Path) -> List[Dict[str, Any]]:
    """
    Load test cases from a JSON file.

    The file may be valid JSON or a Python literal (for bytes support).
    Returns:
        List of test cases, each with 'input' and 'expected_output' keys
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # First try JSON parsing
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # If JSON fails, try Python literal evaluation
        # First, preprocess the content to convert JSON literals to Python literals
        # Replace JSON true/false/null with Python True/False/None
        # Also handle byte literals that might be malformed
        processed_content = content
        # Replace JSON literals (must be whole words to avoid replacing inside strings)
        # Use regex to replace true/false/null not inside quotes
        # Simple approach: replace all occurrences (risky but works for this format)
        processed_content = processed_content.replace('true', 'True')
        processed_content = processed_content.replace('false', 'False')
        processed_content = processed_content.replace('null', 'None')

        try:
            data = ast.literal_eval(processed_content)
        except (SyntaxError, ValueError) as e:
            # Try one more approach: parse as JSON with a custom decoder
            # Or try to manually parse the mixed format
            raise ValueError(f"Failed to parse {json_path} as JSON or Python literal: {e}") from e

    # Convert bytes literals (if any)
    data = eval_bytes_literals(data)

    # Extract cases
    cases = data.get('cases', [])
    return cases


def run_feature1_test(input_data: Dict[str, Any]) -> List[str]:
    """
    Run FileFinder test.

    Args:
        input_data: Dictionary with FileFinder parameters

    Returns:
        List of file paths
    """
    finder = filefinder.FileFinder(
        roots=input_data['roots'],
        recurse=input_data.get('recurse', True),
        ignore_dirs=input_data.get('ignore_dirs'),
        find_only_text_files=input_data.get('find_only_text_files', False),
        search_extensions=input_data.get('search_extensions'),
        ignore_extensions=input_data.get('ignore_extensions'),
        search_patterns=input_data.get('search_patterns'),
        ignore_patterns=input_data.get('ignore_patterns'),
        filter_include_patterns=input_data.get('filter_include_patterns'),
        filter_exclude_patterns=input_data.get('filter_exclude_patterns'),
    )
    return list(finder.files())


def run_feature2_test(input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run ContentMatcher test.

    Args:
        input_data: Dictionary with pattern, flags, and content

    Returns:
        List of MatchResult-like dicts
    """
    results = matcher.matcher(
        pattern=input_data['pattern'],
        ignore_case=input_data.get('ignore_case', False),
        smart_case=input_data.get('smart_case', False),
        whole_words=input_data.get('whole_words', False),
        literal_pattern=input_data.get('literal_pattern', False),
        invert_match=input_data.get('invert_match', False),
        max_match_count=input_data.get('max_match_count'),
        content=input_data['content'],
    )
    # Convert MatchResult objects to dicts
    output = []
    for r in results:
        output.append({
            'matching_line': r.matching_line,
            'matching_lineno': r.matching_lineno,
            'matching_column_ranges': r.matching_column_ranges,
        })
    return output


def run_feature3_test(input_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
    """
    Run OutputFormatter test.

    Args:
        input_data: Dictionary with formatter, actions, and colors

    Returns:
        String for default formatter, dict for JSON formatter
    """
    return formatter.format_output(
        formatter_name=input_data['formatter'],
        actions=input_data['actions'],
        colors=input_data.get('colors', False),
    )


def run_feature4_test(input_data: List[str]) -> Dict[str, Any]:
    """
    Run CLI argument parsing test.

    Args:
        input_data: List of command-line arguments

    Returns:
        Dictionary of parsed parameters
    """
    # parse_args expects argument list without program name (sys.argv[1:])
    return cli.parse_args(input_data)


def run_feature5_test(input_data: Dict[str, Any]) -> Any:
    """
    Run cross-platform utilities test.

    Args:
        input_data: Dictionary with 'function' and parameters

    Returns:
        Result of the utility function
    """
    func_name = input_data['function']

    if func_name == 'istextfile':
        bytes_data = input_data['bytes_data']
        blocksize = input_data.get('blocksize', 512)
        return utils.istextfile(bytes_data, blocksize)

    elif func_name == 'tostring':
        data = input_data['data']
        return utils.tostring(data)

    elif func_name == 'decode_colorama_color':
        color_str = input_data['color_str']
        return utils.decode_colorama_color(color_str)

    elif func_name == 'normalize_path':
        path = input_data['path']
        platform = input_data['platform']
        return utils.normalize_path(path, platform)

    else:
        raise ValueError(f"Unknown function: {func_name}")


def serialize_output(output: Any) -> str:
    """
    Serialize output to string for writing to file.

    For strings, returns as-is.
    For other types, returns JSON representation.
    """
    if isinstance(output, str):
        return output
    else:
        return json.dumps(output, indent=2)


def run_test_suite():
    """Run all test cases and write outputs to stdout directory."""
    test_cases_dir = Path(__file__).parent / 'test_cases'
    stdout_dir = Path(__file__).parent / 'stdout'

    # Create stdout directory if it doesn't exist
    stdout_dir.mkdir(exist_ok=True)

    # Map feature file prefixes to test functions
    test_handlers = {
        'feature1_file_discovery': run_feature1_test,
        'feature2_content_matching': run_feature2_test,
        'feature3_output_formatting': run_feature3_test,
        'feature4_cli': run_feature4_test,
        'feature5_cross_platform': run_feature5_test,
    }

    # Process each JSON file
    for json_file in test_cases_dir.glob('*.json'):
        print(f"Processing {json_file.name}...")

        # Determine which handler to use based on filename prefix
        handler = None
        for prefix, h in test_handlers.items():
            if json_file.stem.startswith(prefix):
                handler = h
                break

        if not handler:
            print(f"Warning: No handler for {json_file.name}", file=sys.stderr)
            continue

        # Load test cases
        try:
            cases = load_test_cases(json_file)
        except Exception as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)
            continue

        # Run each case
        for i, case in enumerate(cases):
            try:
                input_data = case['input']
                output = handler(input_data)
                output_str = serialize_output(output)

                # Write output file
                output_filename = f"{json_file.stem}@{i:03d}.txt"
                output_path = stdout_dir / output_filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_str)

                print(f"  Wrote case {i} to {output_filename}")

            except Exception as e:
                print(f"Error running case {i} in {json_file}: {e}", file=sys.stderr)
                # Write error message to output file for debugging
                output_filename = f"{json_file.stem}@{i:03d}.txt"
                output_path = stdout_dir / output_filename
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"ERROR: {e}")

    print("Test suite completed.")


if __name__ == '__main__':
    run_test_suite()