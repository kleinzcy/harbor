# GitIngest - Automated Code Repository Analysis Tool

## Project Goal

Build a Python tool that automatically analyzes code repositories by parsing local directories and remote Git repositories (GitHub, GitLab, Bitbucket), extracting structured summaries with intelligent content extraction and directory tree generation. This tool allows developers to quickly understand repository structure and content without manually navigating through files, while providing AI-ready formatted output for further processing.

---

## Background & Problem

Without this library/tool, developers are forced to manually clone repositories, navigate directory structures, filter files based on patterns, and extract relevant content. This leads to repetitive code, error-prone boilerplate, maintenance issues when dealing with different Git platforms, and significant time investment for repository analysis.

With this library/tool, developers can automate the entire repository analysis process with a simple API call or command line interface. It provides intelligent filtering, supports multiple Git platforms, handles various file formats including Jupyter notebooks, and generates structured output ready for AI processing or documentation.

---

## Core Features

### Feature 1: Repository Cloning

**As a developer**, I want to clone Git repositories from various platforms with authentication support, so I can analyze both public and private repositories programmatically.

**Expected Behavior / Usage:**

The cloning feature should support:
- Public repository cloning from GitHub, GitLab, Bitbucket
- Private repository cloning with authentication tokens
- Branch-specific cloning
- Sparse checkout for monorepo subdirectories
- Configurable clone depth and timeout settings

**Test Cases:** `tests/test_cases/feature1_repository_cloning.json`

```json
{
    "description": "Test various repository cloning scenarios",
    "cases": [
        {
            "input": {
                "url": "https://github.com/octocat/Hello-World",
                "local_path": "/tmp/test-repo",
                "branch": "main"
            },
            "expected_output": {
                "success": true,
                "git_dir_exists": true,
                "readme_exists": true
            }
        },
        {
            "input": {
                "url": "https://github.com/user/private-repo",
                "local_path": "/tmp/private",
                "branch": "develop",
                "token": "ghp_xxxxxxxxxxxxx"
            },
            "expected_output": {
                "success": true,
                "git_dir_exists": true,
                "branch": "develop"
            }
        },
        {
            "input": {
                "url": "https://github.com/user/monorepo",
                "local_path": "/tmp/sparse",
                "subpath": "/packages/frontend"
            },
            "expected_output": {
                "success": true,
                "subpath_exists": true,
                "other_dirs_excluded": true
            }
        }
    ]
}
```

---

### Feature 2: File System Scanning

**As a developer**, I want to scan directories and extract file contents with intelligent filtering, so I can focus on relevant files and ignore noise.

**Expected Behavior / Usage:**

The file scanning feature should:
- Recursively scan directories with configurable depth
- Apply include/exclude patterns (glob patterns)
- Respect .gitignore files automatically
- Handle file size limits with graceful truncation
- Extract file contents with proper encoding detection
- Generate directory tree visualization

**Test Cases:** `tests/test_cases/feature2_file_scanning.json`

```json
{
    "description": "Test file system scanning with various filtering options",
    "cases": [
        {
            "input": {
                "local_path": "/tmp/test-scan",
                "files": {
                    "file1.py": "print('hello')",
                    "file2.txt": "text content"
                },
                "ignore_patterns": []
            },
            "expected_output": {
                "files_found": 2,
                "contains_python": true,
                "contains_text": true
            }
        },
        {
            "input": {
                "local_path": "/tmp/test-filter",
                "files": {
                    "keep.py": "keep this",
                    "ignore.pyc": "ignore this"
                },
                "ignore_patterns": ["*.pyc"]
            },
            "expected_output": {
                "files_found": 1,
                "contains_keep": true,
                "contains_ignore": false
            }
        },
        {
            "input": {
                "local_path": "/tmp/test-size",
                "files": {
                    "small.txt": "x".repeat(100),
                    "large.txt": "x".repeat(1000000)
                },
                "max_file_size": 1000
            },
            "expected_output": {
                "small_included": true,
                "large_truncated": true,
                "size_limit_respected": true
            }
        }
    ]
}
```

---

### Feature 3: Jupyter Notebook Processing

**As a developer**, I want to convert Jupyter notebooks to readable code format, so I can include notebook analysis in repository summaries.

**Expected Behavior / Usage:**

The notebook processing feature should:
- Parse .ipynb files and extract code cells
- Convert markdown cells to comments
- Optionally include cell outputs
- Handle malformed notebooks gracefully
- Support different notebook versions

**Test Cases:** `tests/test_cases/feature3_notebook_processing.json`

```json
{
    "description": "Test Jupyter notebook conversion to executable Python code",
    "cases": [
        {
            "input": {
                "notebook": {
                    "cells": [
                        {
                            "cell_type": "code",
                            "source": ["import math\n", "print(math.pi)"],
                            "outputs": [{"text": "3.141592653589793\n"}]
                        },
                        {
                            "cell_type": "markdown",
                            "source": ["# Title\n", "Description"]
                        }
                    ]
                },
                "include_output": true
            },
            "expected_output": {
                "contains_import": true,
                "contains_print": true,
                "contains_output": true,
                "contains_markdown": true
            }
        },
        {
            "input": {
                "notebook": {
                    "cells": [{
                        "cell_type": "code",
                        "source": ["x = 42"],
                        "outputs": [{"text": "42"}]
                    }]
                },
                "include_output": false
            },
            "expected_output": {
                "contains_code": true,
                "excludes_output": true
            }
        }
    ]
}
```

---

### Feature 4: Web API Interface

**As a user**, I want to analyze repositories through a web interface, so I can integrate repository analysis into web applications.

**Expected Behavior / Usage:**

The web API should provide:
- RESTful endpoints for repository ingestion
- Authentication support for private repositories
- Configurable filtering options via JSON payload
- Asynchronous processing with status tracking
- Digest generation and retrieval

**Test Cases:** `tests/test_cases/feature4_web_api.json`

```json
{
    "description": "Test web API endpoints for repository ingestion",
    "cases": [
        {
            "input": {
                "endpoint": "/api/ingest",
                "method": "POST",
                "payload": {
                    "input_text": "https://github.com/octocat/Hello-World",
                    "max_file_size": 5120,
                    "pattern_type": "exclude",
                    "pattern": "",
                    "token": null
                }
            },
            "expected_output": {
                "status_code": 200,
                "has_summary": true,
                "has_tree": true,
                "has_content": true,
                "contains_repo_name": true
            }
        },
        {
            "input": {
                "endpoint": "/api/ingest",
                "method": "POST",
                "payload": {
                    "input_text": "https://github.com/user/private",
                    "max_file_size": 5120,
                    "pattern_type": "exclude",
                    "pattern": "",
                    "token": null
                }
            },
            "expected_output": {
                "status_code": 400,
                "error_contains_auth": true
            }
        },
        {
            "input": {
                "endpoint": "/api/ingest",
                "method": "POST",
                "payload": {
                    "input_text": "https://github.com/user/repo",
                    "max_file_size": 5120,
                    "pattern_type": "include",
                    "pattern": "*.py,*.md",
                    "token": null
                }
            },
            "expected_output": {
                "status_code": 200,
                "includes_py_md": true,
                "excludes_other_formats": true
            }
        }
    ]
}
```

---

### Feature 5: Command Line Interface

**As a developer**, I want to use GitIngest from the command line, so I can quickly analyze repositories without writing Python code.

**Expected Behavior / Usage:**

The CLI should support:
- Local directory analysis
- Remote repository URL analysis
- Configurable filtering patterns
- Output to file or stdout
- Authentication via environment variables
- Branch and subpath specifications

**Test Cases:** `tests/test_cases/feature5_cli_interface.json`

```json
{
    "description": "Test command line interface functionality",
    "cases": [
        {
            "input": {
                "command": ["gitingest", "/tmp/test-project"],
                "working_dir": "/tmp"
            },
            "expected_output": {
                "exit_code": 0,
                "creates_digest": true,
                "contains_structure": true
            }
        },
        {
            "input": {
                "command": ["gitingest", "https://github.com/octocat/Hello-World"],
                "working_dir": "/tmp"
            },
            "expected_output": {
                "exit_code": 0,
                "creates_digest": true,
                "contains_hello_world": true
            }
        },
        {
            "input": {
                "command": [
                    "gitingest", ".",
                    "--exclude-pattern", "*.pyc",
                    "--exclude-pattern", "__pycache__/",
                    "--include-pattern", "*.py"
                ],
                "working_dir": "/tmp/test-project"
            },
            "expected_output": {
                "exit_code": 0,
                "includes_py": true,
                "excludes_pyc": true
            }
        },
        {
            "input": {
                "command": ["gitingest", ".", "--output", "-"],
                "working_dir": "/tmp/test-project"
            },
            "expected_output": {
                "exit_code": 0,
                "stdout_contains_structure": true,
                "no_digest_file": true
            }
        }
    ]
}
```

---

### Feature 6: Intelligent Content Extraction

**As a developer**, I want intelligent content extraction with language-specific parsing, so I can get meaningful code summaries instead of raw file dumps.

**Expected Behavior / Usage:**

*6.1 Python Code Analysis — Extract imports, functions, and classes*

The Python analyzer should:
- Parse Python files and extract import statements
- Identify function and class definitions
- Extract docstrings and comments
- Handle different Python versions and syntax

**Test Cases:** `tests/test_cases/feature6_1_python_analysis.json`

```json
{
    "description": "Test Python code analysis and extraction",
    "cases": [
        {
            "input": {
                "code": "import os\nimport sys\n\ndef hello():\n    \"\"\"Say hello\"\"\"\n    print('Hello')\n\nclass Calculator:\n    def add(self, a, b):\n        return a + b"
            },
            "expected_output": {
                "imports": ["os", "sys"],
                "functions": ["hello"],
                "classes": ["Calculator"],
                "has_docstring": true
            }
        }
    ]
}
```

*6.2 Configuration File Parsing — Extract key-value pairs from config files*

The config parser should:
- Parse common config formats (JSON, YAML, TOML, INI)
- Extract key-value pairs for summary
- Handle nested structures
- Support environment variable substitution detection

**Test Cases:** `tests/test_cases/feature6_2_config_parsing.json`

```json
{
    "description": "Test configuration file parsing and extraction",
    "cases": [
        {
            "input": {
                "format": "json",
                "content": "{\"name\": \"project\", \"version\": \"1.0.0\", \"dependencies\": {\"requests\": \"^2.28.0\"}}"
            },
            "expected_output": {
                "keys": ["name", "version", "dependencies"],
                "values": ["project", "1.0.0", {"requests": "^2.28.0"}]
            }
        },
        {
            "input": {
                "format": "yaml",
                "content": "name: project\nversion: 1.0.0\ndependencies:\n  - requests\n  - pytest"
            },
            "expected_output": {
                "keys": ["name", "version", "dependencies"],
                "values": ["project", "1.0.0", ["requests", "pytest"]]
            }
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_[name].json` should write its output to `tests/stdout/feature1_[name]@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.

**Additional Deliverables:**
- Complete Python package with proper module structure
- Comprehensive documentation including API reference and usage examples
- Docker container for easy deployment
- CI/CD pipeline configuration for automated testing
- Performance benchmarks for large repository analysis
- Security audit report for authentication handling