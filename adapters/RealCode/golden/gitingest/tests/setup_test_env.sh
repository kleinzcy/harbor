#!/bin/bash
# Setup test environment for GitIngest tests
# Creates local Git repositories for testing without GitHub access

set -e

echo "Setting up test environment..."

# Create a local Git repository for testing
TEST_REPO="/tmp/test-local-repo"

if [ -d "$TEST_REPO" ]; then
    echo "Removing existing test repository..."
    rm -rf "$TEST_REPO"
fi

echo "Creating test repository at $TEST_REPO..."
mkdir -p "$TEST_REPO"
cd "$TEST_REPO"

# Initialize Git repository
git init

# Create test files
echo "# Test Repository" > README.md
echo "print('hello world')" > test.py
echo "def add(a, b):" >> test.py
echo "    return a + b" >> test.py

mkdir -p src
echo "module.exports = {}" > src/index.js

mkdir -p docs
echo "Documentation" > docs/guide.md

# Create a config file
echo '{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "requests": "^2.28.0"
  }
}' > config.json

# Create a Python package structure
mkdir -p mypackage
echo "def hello():" > mypackage/__init__.py
echo "    print('Hello from package')" >> mypackage/__init__.py

# Add and commit all files
git add .
git commit -m "Initial commit with test files"

echo "Test repository created successfully at $TEST_REPO"

# Create a test project directory for file scanning tests
TEST_PROJECT="/tmp/test-project"
if [ -d "$TEST_PROJECT" ]; then
    echo "Removing existing test project..."
    rm -rf "$TEST_PROJECT"
fi

echo "Creating test project at $TEST_PROJECT..."
mkdir -p "$TEST_PROJECT"
cd "$TEST_PROJECT"

# Create various file types
echo "Python source file" > main.py
echo "Python compiled file" > module.pyc
echo "Text file" > notes.txt
echo "Markdown file" > README.md

mkdir -p __pycache__
echo "Cache file" > __pycache__/cache.pyo

mkdir -p src
echo "Source code" > src/utils.py

echo "Test project created successfully at $TEST_PROJECT"

echo ""
echo "Test environment setup complete!"
echo ""
echo "Available test resources:"
echo "1. Local Git repository: $TEST_REPO"
echo "2. Test project directory: $TEST_PROJECT"
echo "3. Non-existent repository: /tmp/nonexistent-repo"
echo ""
echo "You can now run tests without GitHub access."