import sys
sys.path.insert(0, '.')
from tests.test_runner import run_feature1_test

input_data = {
    "roots": ["./test_data"],
    "recurse": True,
    "ignore_dirs": [".git", "__pycache__", ".svn"],
    "find_only_text_files": True,
    "search_extensions": [".py", ".js", ".ts"],
    "ignore_extensions": [".min.js"],
    "search_patterns": ["test_*"],
    "ignore_patterns": ["*_temp.*"],
    "filter_include_patterns": ["src/**"],
    "filter_exclude_patterns": ["src/vendor/**"]
}
output = run_feature1_test(input_data)
print('Output:', output)
print('Expected:', ['./test_data/src/main.py', './test_data/src/test_module.py', './test_data/src/utils.js'])