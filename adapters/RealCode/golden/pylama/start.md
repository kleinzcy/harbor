# Pylama - Python Code Quality Auditing Tool

## Project Goal

Build a command-line tool for Python code quality auditing that integrates multiple code checkers and static analysis tools to conduct comprehensive quality checks on Python code. The tool allows developers to detect syntax errors, code style violations, potential bugs, code complexity, and missing documentation through a unified interface without manually invoking multiple linters or managing separate configurations.

---

## Background & Problem

Without this library/tool, developers are forced to manually run multiple separate linters (pycodestyle, pyflakes, mccabe, pydocstyle, pylint, mypy, etc.) with different configuration formats and command-line interfaces. This leads to repetitive boilerplate code, inconsistent configuration management, difficulty in aggregating results, and maintenance overhead when updating tool versions or adding new checks.

With this library/tool, developers can use a single command to run all required checks, manage configurations centrally through INI or TOML files, receive unified error reports in multiple formats, and benefit from asynchronous processing for large codebases—all while maintaining extensibility through a plugin system.

---

## Core Features

### Feature 1: Multi-Linter Integration Engine

**As a developer**, I want to centrally manage and invoke multiple Python code checking tools, so I can get comprehensive code quality feedback from a single command.

**Expected Behavior / Usage:**

The engine should provide a unified interface for registering and executing linters. Each linter (pycodestyle, pyflakes, mccabe, pydocstyle, pylint, mypy, isort, eradicate, vulture, radon) must implement a common `Linter` base class with methods `add_args`, `allow`, and `run_check`. The system should automatically discover and load available linters, allowing users to enable/disable specific checkers via configuration.

**Test Cases:** `tests/test_cases/feature1_linter_integration.json`

```json
{
    "description": "Verify that multiple linters can be registered and executed correctly",
    "cases": [
        {
            "input": {"linters": ["pycodestyle", "pyflakes"], "code": "def foo(): pass"},
            "expected_output": []
        },
        {
            "input": {"linters": ["pycodestyle"], "code": "x=1"},
            "expected_output": [{"source": "pycodestyle", "type": "E", "number": "E225"}]
        }
    ]
}
```

---

### Feature 2: Configuration Management System

**As a developer**, I want to manage all linter configurations through a unified system supporting multiple file formats, so I can maintain consistent settings across tools and environments.

**Expected Behavior / Usage:**

Support INI, TOML, setup.cfg, and pyproject.toml configuration files with hierarchical precedence: command-line arguments > file-specific configuration > linter-specific configuration > global configuration. The system should automatically discover configuration files in parent directories and support environment variable overrides.

**Test Cases:** `tests/test_cases/feature2_config_management.json`

```json
{
    "description": "Test configuration loading and precedence rules",
    "cases": [
        {
            "input": {"config_content": "[pylama]\nlinters = pycodestyle,pyflakes", "cli_args": ["--linters=mccabe"]},
            "expected_output": {"linters": ["mccabe"]}
        },
        {
            "input": {"config_content": "[pylama:pycodestyle]\nmax_line_length = 100", "cli_args": []},
            "expected_output": {"pycodestyle": {"max_line_length": 100}}
        }
    ]
}
```

---

### Feature 3: File Scanning and Filtering

**As a developer**, I want to recursively scan directories with pattern matching and ignore rules, so I can check only relevant Python files in my project.

**Expected Behavior / Usage:**

Provide a `check_paths()` function that accepts file/directory paths, supports glob patterns, excludes files via `.pylamaignore` or configuration, and can read code directly from stdin. The scanner should respect file extensions and skip binary/non-Python files.

**Test Cases:** `tests/test_cases/feature3_file_scanning.json`

```json
{
    "description": "Test file scanning with ignore patterns and path matching",
    "cases": [
        {
            "input": {"paths": ["src/"], "ignore_patterns": ["*/test_*.py"]},
            "expected_output": {"files_found": 5, "files_ignored": 2}
        },
        {
            "input": {"paths": ["-"], "code": "import os"},
            "expected_output": {"files_checked": 1}
        }
    ]
}
```

---

### Feature 4: Error Reporting and Formatting

**As a developer**, I want to receive error reports in multiple formats with configurable sorting and filtering, so I can integrate results into my workflow or CI/CD pipelines.

**Expected Behavior / Usage:**

Support output formats: pydocstyle, pycodestyle, pylint, parsable, json, etc. Errors should include filename, line number, column, error type, code, description, and source linter. Provide options to sort by severity (Fatal, Error, Warning, Convention, Refactor) and filter by error codes.

*4.1 JSON Output — Machine-readable error listing*

**Test Cases:** `tests/test_cases/feature4_1_json_output.json`

```json
{
    "description": "Verify JSON output format contains all required fields",
    "cases": [
        {
            "input": {"format": "json", "code": "x = 1"},
            "expected_output": [{"filename": "<stdin>", "lnum": 1, "col": 3, "source": "pycodestyle", "type": "E", "number": "E225", "text": "missing whitespace around operator"}]
        }
    ]
}
```

*4.2 Human-readable Output — Colored terminal display*

**Test Cases:** `tests/test_cases/feature4_2_human_output.json`

```json
{
    "description": "Verify human-readable format matches expected style",
    "cases": [
        {
            "input": {"format": "pycodestyle", "code": "def foo(): pass"},
            "expected_output": ["stdin:1:1: D100 Missing docstring in public module"]
        }
    ]
}
```

---

### Feature 5: Asynchronous Processing and Performance Optimization

**As a developer**, I want to run linters concurrently and optimize memory usage, so I can check large codebases efficiently.

**Expected Behavior / Usage:**

Implement `check_async()` function that processes multiple files in parallel using multiprocessing or threading. Include caching mechanisms to avoid re-checking unchanged files and memory optimization for large files. Automatically disable linters that don't support async mode (e.g., pylint).

**Test Cases:** `tests/test_cases/feature5_async_processing.json`

```json
{
    "description": "Test asynchronous checking performance and correctness",
    "cases": [
        {
            "input": {"paths": ["large_project/"], "concurrent": true},
            "expected_output": {"time_saved_ratio": ">0.5"}
        },
        {
            "input": {"paths": ["small.py"], "concurrent": false},
            "expected_output": {"errors_count": 0}
        }
    ]
}
```

---

### Feature 6: Command-line Interface

**As a developer**, I want to run checks via a intuitive CLI with comprehensive options, so I can integrate the tool into scripts and development workflows.

**Expected Behavior / Usage:**

Provide a `shell()` function and `pylama` command supporting arguments: `--select`, `--ignore`, `--linters`, `--format`, `--max-line-length`, `--max-complexity`, `--config`, `--verbose`, `--abspath`, `--sort`. The CLI should exit with appropriate status codes and support reading from stdin.

**Test Cases:** `tests/test_cases/feature6_cli_interface.json`

```json
{
    "description": "Test command-line argument parsing and execution",
    "cases": [
        {
            "input": {"args": ["--select=E301", "test.py"]},
            "expected_output": {"exit_code": 0}
        },
        {
            "input": {"args": ["--help"]},
            "expected_output": {"output_contains": "usage:"}
        }
    ]
}
```

---

### Feature 7: Git Hooks Integration

**As a developer**, I want to install pre-commit hooks that automatically check code before commits, so I can catch issues early and maintain code quality standards.

**Expected Behavior / Usage:**

Provide `git_hook()` function to install a Git pre-commit hook that runs configured linters on staged files. Support parameters: `complexity` (max McCabe complexity), `strict` (block commit on errors), `linters` (comma-separated list). Return appropriate exit codes and user-friendly messages.

**Test Cases:** `tests/test_cases/feature7_git_hooks.json`

```json
{
    "description": "Test Git hook installation and execution",
    "cases": [
        {
            "input": {"action": "install", "complexity": 10, "strict": true},
            "expected_output": {"hook_installed": true}
        },
        {
            "input": {"action": "run", "staged_files": ["bad.py"]},
            "expected_output": {"errors_found": 2, "commit_blocked": true}
        }
    ]
}
```

---

### Feature 8: Error Handling and Deduplication

**As a developer**, I want duplicate errors from multiple linters to be automatically deduplicated, so I get clean, actionable feedback without redundancy.

**Expected Behavior / Usage:**

Implement `Error` class with attributes: filename, lnum, col, number, text, type, source. Provide `remove_duplicates()` function that identifies and merges identical errors from different linters based on location and error code.

**Test Cases:** `tests/test_cases/feature8_error_deduplication.json`

```json
{
    "description": "Test error deduplication across multiple linters",
    "cases": [
        {
            "input": {"errors": [
                {"source": "pycodestyle", "lnum": 10, "col": 5, "text": "E701"},
                {"source": "pylint", "lnum": 10, "col": 5, "text": "C0321"}
            ]},
            "expected_output": [{"source": "pycodestyle", "lnum": 10, "col": 5, "text": "E701"}]
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_[name].json` should write its output to `tests/stdout/feature1_[name]@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.