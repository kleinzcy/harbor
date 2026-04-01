#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tests.test_runner import load_test_cases, run_feature4_test, run_feature5_test

def enhance_feature4():
    orig_path = Path('tests/test_cases/feature4_cli.json')
    cases = load_test_cases(orig_path)
    new_cases = []
    def compute(input_data):
        return run_feature4_test(input_data)

    # Case 6: no pattern, no roots (defaults)
    new_cases.append({
        "input": [],
        "expected_output": compute([])
    })
    # Case 7: pattern with leading dash, using -- separator
    new_cases.append({
        "input": ["--", "-help", "."],
        "expected_output": compute(["--", "-help", "."])
    })
    # Case 8: negative context (should be allowed?)
    new_cases.append({
        "input": ["-C", "-1", "hello", "."],
        "expected_output": compute(["-C", "-1", "hello", "."])
    })
    # Case 9: zero context
    new_cases.append({
        "input": ["-C", "0", "hello", "."],
        "expected_output": compute(["-C", "0", "hello", "."])
    })
    # Case 10: --no-recurse flag
    new_cases.append({
        "input": ["--no-recurse", "hello", "."],
        "expected_output": compute(["--no-recurse", "hello", "."])
    })
    # Case 11: --textonly flag
    new_cases.append({
        "input": ["--textonly", "hello", "."],
        "expected_output": compute(["--textonly", "hello", "."])
    })
    # Case 12: --color and --no-color
    new_cases.append({
        "input": ["--color", "hello", "."],
        "expected_output": compute(["--color", "hello", "."])
    })
    new_cases.append({
        "input": ["--no-color", "hello", "."],
        "expected_output": compute(["--no-color", "hello", "."])
    })
    # Case 13: --json output flag (not in expected dict, but parse_args includes 'json' key)
    new_cases.append({
        "input": ["--json", "hello", "."],
        "expected_output": compute(["--json", "hello", "."])
    })
    # Case 14: multiple include-type flags
    new_cases.append({
        "input": ["--include-type", "python", "--include-type", "cpp", "hello", "."],
        "expected_output": compute(["--include-type", "python", "--include-type", "cpp", "hello", "."])
    })
    # Case 15: exclude-type flag
    new_cases.append({
        "input": ["--exclude-type", "python", "hello", "."],
        "expected_output": compute(["--exclude-type", "python", "hello", "."])
    })
    # Case 16: language flag --python
    new_cases.append({
        "input": ["--python", "hello", "."],
        "expected_output": compute(["--python", "hello", "."])
    })
    # Skip conflicting flags -i -s
    # Skip unknown flag

    enhanced_cases = cases + new_cases
    enhanced = {
        "description": "Command‑line argument parsing into pss_run parameters (enhanced with edge cases)",
        "cases": enhanced_cases
    }
    output_path = Path('tests/enhanced_test_cases/feature4_cli.json')
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced, f, indent=4)
    print(f"Enhanced feature4 written to {output_path}")

def bytes_to_str_repr(b):
    """Convert bytes to string representation like b'...' for JSON storage."""
    # Use repr to get b'...' format, then ensure it's a string
    return repr(b)

def convert_bytes_to_str(obj):
    """Recursively convert bytes objects to string representations for JSON serialization."""
    if isinstance(obj, bytes):
        return bytes_to_str_repr(obj)
    elif isinstance(obj, dict):
        return {k: convert_bytes_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_bytes_to_str(item) for item in obj]
    else:
        return obj

def enhance_feature5():
    orig_path = Path('tests/test_cases/feature5_cross_platform.json')
    cases = load_test_cases(orig_path)
    new_cases = []

    # Helper function to compute expected output
    def compute(input_data):
        # input_data may contain bytes objects (from load_test_cases) or string representations
        # run_feature5_test expects actual bytes objects where needed
        # Since we're calling compute with input_data that may have bytes objects,
        # we can pass it directly
        return run_feature5_test(input_data)

    # Case 8: istextfile with empty bytes
    new_cases.append({
        "input": {
            "function": "istextfile",
            "bytes_data": b"",
            "blocksize": 512
        },
        "expected_output": compute({
            "function": "istextfile",
            "bytes_data": b"",
            "blocksize": 512
        })
    })
    # Case 9: istextfile with blocksize smaller than data
    new_cases.append({
        "input": {
            "function": "istextfile",
            "bytes_data": b"hello" * 200,
            "blocksize": 100
        },
        "expected_output": compute({
            "function": "istextfile",
            "bytes_data": b"hello" * 200,
            "blocksize": 100
        })
    })
    # Case 10: istextfile with control characters (tab, newline ok)
    new_cases.append({
        "input": {
            "function": "istextfile",
            "bytes_data": b"\t\n\r\x0c",
            "blocksize": 512
        },
        "expected_output": compute({
            "function": "istextfile",
            "bytes_data": b"\t\n\r\x0c",
            "blocksize": 512
        })
    })
    # Case 11: istextfile with binary control character (0x01)
    new_cases.append({
        "input": {
            "function": "istextfile",
            "bytes_data": b"\x01",
            "blocksize": 512
        },
        "expected_output": compute({
            "function": "istextfile",
            "bytes_data": b"\x01",
            "blocksize": 512
        })
    })
    # Case 12: tostring with bytes not UTF-8 (fallback)
    new_cases.append({
        "input": {
            "function": "tostring",
            "data": b"\xff\xfe"
        },
        "expected_output": compute({
            "function": "tostring",
            "data": b"\xff\xfe"
        })
    })
    # Case 14: decode_colorama_color with unknown color
    new_cases.append({
        "input": {
            "function": "decode_colorama_color",
            "color_str": "UNKNOWN"
        },
        "expected_output": compute({
            "function": "decode_colorama_color",
            "color_str": "UNKNOWN"
        })
    })
    # Case 15: decode_colorama_color with empty string
    new_cases.append({
        "input": {
            "function": "decode_colorama_color",
            "color_str": ""
        },
        "expected_output": compute({
            "function": "decode_colorama_color",
            "color_str": ""
        })
    })
    # Case 16: normalize_path with relative path
    new_cases.append({
        "input": {
            "function": "normalize_path",
            "path": ".././dir/file.py",
            "platform": "linux"
        },
        "expected_output": compute({
            "function": "normalize_path",
            "path": ".././dir/file.py",
            "platform": "linux"
        })
    })
    # Case 17: normalize_path with trailing slash
    new_cases.append({
        "input": {
            "function": "normalize_path",
            "path": "/home/user/",
            "platform": "linux"
        },
        "expected_output": compute({
            "function": "normalize_path",
            "path": "/home/user/",
            "platform": "linux"
        })
    })
    # Case 18: normalize_path with mixed slashes on windows (already covered)
    # Case 19: normalize_path with platform 'posix'
    new_cases.append({
        "input": {
            "function": "normalize_path",
            "path": "/home//user",
            "platform": "posix"
        },
        "expected_output": compute({
            "function": "normalize_path",
            "path": "/home//user",
            "platform": "posix"
        })
    })

    # Convert all bytes objects to string representations for JSON serialization
    enhanced_cases = convert_bytes_to_str(cases + new_cases)

    enhanced = {
        "description": "Cross‑platform utilities: text detection, byte conversion, color decoding, path normalization (enhanced with edge cases)",
        "cases": enhanced_cases
    }
    output_path = Path('tests/enhanced_test_cases/feature5_cross_platform.json')
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced, f, indent=4)
    print(f"Enhanced feature5 written to {output_path}")

if __name__ == '__main__':
    enhance_feature4()
    enhance_feature5()