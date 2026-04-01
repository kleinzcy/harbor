# PSS (Python Source Search) - Intelligent Source Code Search Tool

## Project Goal

Build a Python command-line tool for source code search that allows developers to recursively search source code files in a directory tree and perform intelligent content matching without manually writing boilerplate code for file discovery, type filtering, and pattern matching. The tool provides efficient file discovery and precise content matching with support for over 40 programming languages, multiple search modes, colored output, and a rich command-line interface.

---

## Background & Problem

Without this library/tool, developers are forced to write custom scripts combining `find`, `grep`, and `awk` commands with complex regular expressions and file filtering logic. This leads to repetitive code, error-prone boilerplate, maintenance issues across different platforms, and lack of consistent output formatting. Manually skipping version control directories, detecting binary files, and handling various file encodings adds significant overhead.

With this library/tool, developers can perform sophisticated source code searches with a simple, unified API or command-line interface. It automatically handles file type detection, recursive traversal, intelligent filtering, and provides colored, structured output — reducing search time and improving code exploration productivity.

---

## Core Features

### Feature 1: Intelligent File Discovery

**As a developer**, I want to recursively search directories for source code files of specific types, so I can focus on relevant files without manual filtering.

**Expected Behavior / Usage:**

The FileFinder class should traverse directory trees, automatically skip version control directories (`.git`, `.svn`), and filter files by extension, name patterns, and text/binary detection. It supports inclusion/exclusion rules for extensions and patterns, and can be configured to search only text files. The `files()` method yields matching file paths.

**Test Cases:** `tests/test_cases/feature1_file_discovery.json`

```json
{
    "description": "FileFinder with extension filtering, ignored directories, and text‑file detection",
    "cases": [
        {
            "input": {
                "roots": ["./test_data"],
                "recurse": true,
                "ignore_dirs": [".git", "__pycache__", ".svn"],
                "find_only_text_files": true,
                "search_extensions": [".py", ".js", ".ts"],
                "ignore_extensions": [".min.js"],
                "search_patterns": ["test_*"],
                "ignore_patterns": ["*_temp.*"],
                "filter_include_patterns": ["src/**"],
                "filter_exclude_patterns": ["src/vendor/**"]
            },
            "expected_output": [
                "./test_data/src/main.py",
                "./test_data/src/test_module.py",
                "./test_data/src/utils.js"
            ]
        },
        {
            "input": {
                "roots": ["./test_data", "./another"],
                "recurse": false,
                "search_extensions": [".txt", ".md"],
                "find_only_text_files": false
            },
            "expected_output": [
                "./test_data/README.md",
                "./test_data/notes.txt",
                "./another/CHANGELOG.txt"
            ]
        }
    ]
}
```

---

### Feature 2: Advanced Content Matching

**As a developer**, I want to search file contents with multiple matching modes (regex, case‑insensitive, whole‑word, inverted), so I can locate code patterns precisely.

**Expected Behavior / Usage:**

The ContentMatcher class compiles a search pattern with flags for case sensitivity, smart‑case (auto‑detect), whole‑word matching, literal interpretation, and inversion. The `matcher()` method reads a file object and yields MatchResult objects containing line numbers, matching lines, and column ranges. It supports maximum match count limiting per file.

**Test Cases:** `tests/test_cases/feature2_content_matching.json`

```json
{
    "description": "ContentMatcher with regex, literal, case‑insensitive, whole‑word, inverted, smart‑case, and max‑match options",
    "cases": [
        {
            "input": {
                "pattern": "def ",
                "ignore_case": false,
                "invert_match": false,
                "whole_words": false,
                "literal_pattern": false,
                "max_match_count": 2,
                "content": "def foo():\n  print('def')\ndef bar():\n  pass\n  # def not here"
            },
            "expected_output": [
                {
                    "matching_line": "def foo():",
                    "matching_lineno": 1,
                    "matching_column_ranges": [[0, 4]]
                },
                {
                    "matching_line": "def bar():",
                    "matching_lineno": 3,
                    "matching_column_ranges": [[0, 4]]
                }
            ]
        },
        {
            "input": {
                "pattern": "vector *<",
                "ignore_case": false,
                "whole_words": false,
                "literal_pattern": false,
                "content": "vector<int> v;\nvector <float> f;"
            },
            "expected_output": [
                {
                    "matching_line": "vector<int> v;",
                    "matching_lineno": 1,
                    "matching_column_ranges": [[0, 10]]
                },
                {
                    "matching_line": "vector <float> f;",
                    "matching_lineno": 2,
                    "matching_column_ranges": [[0, 13]]
                }
            ]
        },
        {
            "input": {
                "pattern": "error",
                "ignore_case": true,
                "invert_match": true,
                "max_match_count": 100,
                "content": "ERROR: something\nWarning: something\nInfo: something"
            },
            "expected_output": [
                {
                    "matching_line": "Warning: something",
                    "matching_lineno": 2,
                    "matching_column_ranges": []
                },
                {
                    "matching_line": "Info: something",
                    "matching_lineno": 3,
                    "matching_column_ranges": []
                }
            ]
        },
        {
            "input": {
                "pattern": "Error",
                "smart_case": true,
                "content": "Error: something\nerror: something\nERROR: something"
            },
            "expected_output": [
                {
                    "matching_line": "Error: something",
                    "matching_lineno": 1,
                    "matching_column_ranges": [[0, 5]]
                }
            ]
        },
        {
            "input": {
                "pattern": "error",
                "smart_case": true,
                "content": "Error: something\nerror: something\nERROR: something"
            },
            "expected_output": [
                {
                    "matching_line": "Error: something",
                    "matching_lineno": 1,
                    "matching_column_ranges": [[0, 5]]
                },
                {
                    "matching_line": "error: something",
                    "matching_lineno": 2,
                    "matching_column_ranges": [[0, 5]]
                },
                {
                    "matching_line": "ERROR: something",
                    "matching_lineno": 3,
                    "matching_column_ranges": [[0, 5]]
                }
            ]
        },
        {
            "input": {
                "pattern": "$\\t",
                "literal_pattern": true,
                "content": "$\\t is a tab"
            },
            "expected_output": [
                {
                    "matching_line": "$\\t is a tab",
                    "matching_lineno": 1,
                    "matching_column_ranges": [[0, 3]]
                }
            ]
        }
    ]
}
```

---

### Feature 3: Flexible Output Formatting

**As a developer**, I want to customize how search results are displayed (colored, structured, JSON, etc.), so I can integrate with other tools or improve readability.

**Expected Behavior / Usage:**

The OutputFormatter abstract base class defines callbacks for start/end of file matching, matching lines, context lines, and binary file messages. DefaultPssOutputFormatter provides colored terminal output with configurable colors for filenames, line numbers, and matches. Users can subclass to produce custom formats (e.g., JSON, XML).

**Test Cases:** `tests/test_cases/feature3_output_formatting.json`

```json
{
    "description": "OutputFormatter callbacks and default colored output",
    "cases": [
        {
            "input": {
                "formatter": "default",
                "actions": [
                    {"type": "start_matches_in_file", "filename": "src/main.py"},
                    {"type": "matching_line", "matchresult": {"matching_line": "def example():", "matching_lineno": 10, "matching_column_ranges": [[0, 3]]}, "filename": "src/main.py"},
                    {"type": "context_line", "line": "import sys", "lineno": 9, "filename": "src/main.py"},
                    {"type": "end_matches_in_file", "filename": "src/main.py"}
                ],
                "colors": false
            },
            "expected_output": "src/main.py\n10:def example():\n 9:import sys"
        },
        {
            "input": {
                "formatter": "json",
                "actions": [
                    {"type": "start_matches_in_file", "filename": "src/main.py"},
                    {"type": "matching_line", "matchresult": {"matching_line": "def example():", "matching_lineno": 10, "matching_column_ranges": [[0, 3]]}, "filename": "src/main.py"},
                    {"type": "end_matches_in_file", "filename": "src/main.py"}
                ]
            },
            "expected_output": {
                "file": "src/main.py",
                "matches": [
                    {"line": 10, "content": "def example():", "columns": [[0, 3]]}
                ]
            }
        },
        {
            "input": {
                "formatter": "default",
                "actions": [
                    {"type": "found_filename", "filename": "src/utils.py"}
                ],
                "colors": true
            },
            "expected_output": "\u001b[36msrc/utils.py\u001b[0m"
        }
    ]
}
```

---

### Feature 4: Comprehensive Command‑Line Interface

**As a developer**, I want to use a rich set of command‑line options to control search behavior, so I can quickly perform ad‑hoc searches without writing code.

**Expected Behavior / Usage:**

The CLI supports options for file type filtering (`--python`, `--cpp`), case sensitivity (`-i`, `-s`), whole‑word matching (`-w`), inverted matching (`-v`), context lines (`-C`), recursion control (`-r`), and output formatting (`--color`, `--no‑color`). It parses arguments, validates them, and drives the search workflow via the `pss_run()` function.

**Test Cases:** `tests/test_cases/feature4_cli.json`

```json
{
    "description": "Command‑line argument parsing into pss_run parameters",
    "cases": [
        {
            "input": ["-i", "-w", "hello", "./src"],
            "expected_output": {
                "pattern": "hello",
                "ignore_case": true,
                "whole_words": true,
                "roots": ["./src"],
                "only_find_files": false,
                "include_types": [],
                "exclude_types": [],
                "recurse": true,
                "textonly": false,
                "ncontext_before": 0,
                "ncontext_after": 0,
                "smart_case": false,
                "invert_match": false,
                "literal_pattern": false
            }
        },
        {
            "input": ["--python", "--cpp", "-f", "./project"],
            "expected_output": {
                "pattern": null,
                "only_find_files": true,
                "roots": ["./project"],
                "include_types": ["python", "cpp"],
                "exclude_types": [],
                "recurse": true,
                "textonly": false,
                "ignore_case": false,
                "whole_words": false,
                "smart_case": false,
                "invert_match": false
            }
        },
        {
            "input": ["-C", "3", "-v", "error", "dir1", "dir2"],
            "expected_output": {
                "pattern": "error",
                "roots": ["dir1", "dir2"],
                "ncontext_before": 3,
                "ncontext_after": 3,
                "invert_match": true,
                "only_find_files": false,
                "include_types": [],
                "exclude_types": [],
                "ignore_case": false,
                "smart_case": false
            }
        },
        {
            "input": ["--literal", "-m", "5", "pattern", "."],
            "expected_output": {
                "pattern": "pattern",
                "literal_pattern": true,
                "max_match_count": 5,
                "roots": ["."],
                "only_find_files": false,
                "ignore_case": false,
                "smart_case": false,
                "whole_words": false
            }
        },
        {
            "input": ["-s", "Error", "./src"],
            "expected_output": {
                "pattern": "Error",
                "smart_case": true,
                "roots": ["./src"],
                "only_find_files": false,
                "include_types": [],
                "exclude_types": [],
                "ignore_case": false,
                "whole_words": false,
                "invert_match": false
            }
        }
    ]
}
```

---

### Feature 5: Cross‑Platform & Performance Optimizations

**As a developer**, I want the tool to work efficiently on Windows, Linux, and macOS, and handle large codebases quickly, so I can rely on it in diverse environments.

**Expected Behavior / Usage:**

The tool uses platform‑aware path handling, encoding detection, and terminal color support. It optimizes searches by caching file lists, using efficient string‑search algorithms for simple patterns, and limiting match counts. The `istextfile()` utility detects binary files; `tostring()` handles byte/string conversions.

**Test Cases:** `tests/test_cases/feature5_cross_platform.json`

```json
{
    "description": "Cross‑platform utilities: text detection, byte conversion, color decoding, path normalization",
    "cases": [
        {
            "input": {
                "function": "istextfile",
                "bytes_data": b"print('hello')\n# comment\n",
                "blocksize": 512
            },
            "expected_output": true
        },
        {
            "input": {
                "function": "istextfile",
                "bytes_data": b"\x00\x01\x02\x03PNG\x1a\n",
                "blocksize": 512
            },
            "expected_output": false
        },
        {
            "input": {
                "function": "tostring",
                "data": b"Hello World"
            },
            "expected_output": "Hello World"
        },
        {
            "input": {
                "function": "tostring",
                "data": "Already a string"
            },
            "expected_output": "Already a string"
        },
        {
            "input": {
                "function": "decode_colorama_color",
                "color_str": "RED,WHITE,BOLD"
            },
            "expected_output": "\u001b[31m\u001b[47m\u001b[1m"
        },
        {
            "input": {
                "function": "normalize_path",
                "path": "C:\\Users\\project\\src\\main.py",
                "platform": "windows"
            },
            "expected_output": "C:/Users/project/src/main.py"
        },
        {
            "input": {
                "function": "normalize_path",
                "path": "/home/user/project/src//main.py",
                "platform": "linux"
            },
            "expected_output": "/home/user/project/src/main.py"
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_[name].json` should write its output to `tests/stdout/feature1_[name]@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.