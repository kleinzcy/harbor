#!/bin/bash
# Simple test runner for GitIngest

# Create output directory
mkdir -p stdout

# Clean previous simple test outputs
rm -f stdout/simple@*.txt 2>/dev/null || true

# Initialize test index
test_index=0

# Function to run a test
run_test() {
    local input="$1"
    local script="$2"

    echo "Running: $script" >&2
    echo "Input: $input" >&2

    # Generate padded index
    padded_index=$(printf "%03d" "$test_index")

    # Define output file
    output_file="stdout/simple@${padded_index}.txt"

    # Run the test and write to output file
    python3 "../gitingest/$script" <<< "$input" > "$output_file"

    echo "Output saved to $output_file" >&2
    echo "---" >&2

    # Increment test index
    test_index=$((test_index + 1))
}

# Feature 1 tests
run_test '{"url": "file:///tmp/test-local-repo", "local_path": "/tmp/test-repo", "branch": "main"}' "feature1_clone.py"
run_test '{"url": "file:///tmp/nonexistent-repo", "local_path": "/tmp/private", "branch": "develop", "token": "ghp_xxxxxxxxxxxxx"}' "feature1_clone.py"
run_test '{"url": "file:///tmp/test-local-repo", "local_path": "/tmp/sparse", "subpath": "/"}' "feature1_clone.py"

# Feature 2 tests  
run_test '{"local_path": "/tmp/test-scan", "files": {"file1.py": "print(\"hello\")", "file2.txt": "text content"}, "ignore_patterns": []}' "feature2_scan.py"
run_test '{"local_path": "/tmp/test-filter", "files": {"keep.py": "keep this", "ignore.pyc": "ignore this"}, "ignore_patterns": ["*.pyc"]}' "feature2_scan.py"

# Feature 3 tests
run_test '{"notebook": {"cells": [{"cell_type": "code", "source": ["import math\n", "print(math.pi)"], "outputs": [{"text": "3.141592653589793\n"}]}, {"cell_type": "markdown", "source": ["# Title\n", "Description"]}]}, "include_output": true}' "feature3_notebook.py"
run_test '{"notebook": {"cells": [{"cell_type": "code", "source": ["x = 42"], "outputs": [{"text": "42"}]}]}, "include_output": false}' "feature3_notebook.py"

# Feature 4 tests
run_test '{"endpoint": "/api/ingest", "method": "POST", "payload": {"input_text": "/tmp/test-local-repo", "max_file_size": 5120, "pattern_type": "exclude", "pattern": "", "token": null}}' "feature4_api.py"
run_test '{"endpoint": "/api/ingest", "method": "POST", "payload": {"input_text": "/tmp/nonexistent-repo", "max_file_size": 5120, "pattern_type": "exclude", "pattern": "", "token": null}}' "feature4_api.py"

# Feature 5 tests
run_test '{"command": ["gitingest", "/tmp/test-project"], "working_dir": "/tmp"}' "feature5_cli.py"
run_test '{"command": ["gitingest", "/tmp/test-local-repo"], "working_dir": "/tmp"}' "feature5_cli.py"

# Feature 6.1 test
run_test '{"code": "import os\nimport sys\n\ndef hello():\n    \"\"\"Say hello\"\"\"\n    print(\"Hello\")\n\nclass Calculator:\n    def add(self, a, b):\n        return a + b"}' "feature6_1_python.py"

# Feature 6.2 tests
run_test '{"format": "json", "content": "{\"name\": \"project\", \"version\": \"1.0.0\", \"dependencies\": {\"requests\": \"^2.28.0\"}}"}' "feature6_2_config.py"
run_test '{"format": "yaml", "content": "name: project\nversion: 1.0.0\ndependencies:\n  - requests\n  - pytest"}' "feature6_2_config.py"

echo "All tests completed." >&2