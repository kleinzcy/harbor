# GitIngest - Automated Code Repository Analysis Tool

GitIngest is a Python tool that automatically analyzes code repositories by parsing local directories and remote Git repositories (GitHub, GitLab, Bitbucket), extracting structured summaries with intelligent content extraction and directory tree generation.

## Features

### 1. Repository Cloning
- Clone Git repositories from various platforms (GitHub, GitLab, Bitbucket)
- Support for authentication tokens for private repositories
- Branch-specific cloning
- Sparse checkout for monorepo subdirectories

### 2. File System Scanning
- Recursive directory scanning with configurable depth
- Intelligent filtering with include/exclude patterns
- Respect .gitignore files automatically
- File size limits with graceful truncation

### 3. Jupyter Notebook Processing
- Convert .ipynb files to readable Python code
- Extract code cells and convert markdown to comments
- Optionally include cell outputs
- Handle malformed notebooks gracefully

### 4. Web API Interface
- RESTful endpoints for repository ingestion
- Authentication support for private repositories
- Configurable filtering options via JSON payload
- Asynchronous processing with status tracking

### 5. Command Line Interface
- Local directory analysis
- Remote repository URL analysis
- Configurable filtering patterns
- Output to file or stdout

### 6. Intelligent Content Extraction
- Python code analysis (imports, functions, classes)
- Configuration file parsing (JSON, YAML, TOML, INI)
- Language-specific parsing for meaningful summaries

## Installation

### From PyPI (Coming Soon)
```bash
pip install gitingest
```

### From Source
```bash
git clone https://github.com/yourusername/gitingest.git
cd gitingest
pip install -e .
```

## Quick Start

### Command Line Usage
```bash
# Analyze local directory
gitingest /path/to/your/project

# Analyze GitHub repository
gitingest https://github.com/octocat/Hello-World

# With filtering options
gitingest . --exclude-pattern "*.pyc" --include-pattern "*.py"

# Output to stdout
gitingest . --output -
```

### Python API Usage
```python
from gitingest.core.cloner import RepositoryCloner
from gitingest.core.scanner import FileScanner

# Clone a repository
cloner = RepositoryCloner()
result = cloner.clone_repository(
    url="https://github.com/octocat/Hello-World",
    branch="main"
)

# Scan a directory
scanner = FileScanner()
result = scanner.scan_directory(
    local_path="/path/to/project",
    ignore_patterns=["*.pyc", "__pycache__/"],
    max_file_size=5120
)
```

### Web API Usage
Start the API server:
```bash
python -m gitingest.api.server
```

Then make requests:
```bash
curl -X POST http://localhost:8080/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "https://github.com/octocat/Hello-World",
    "max_file_size": 5120,
    "pattern_type": "exclude",
    "pattern": ""
  }'
```

## Project Structure

```
gitingest/
├── core/                    # Core functionality
│   ├── cloner.py           # Repository cloning
│   └── scanner.py          # File system scanning
├── parsers/                # Content parsers
│   ├── notebook_parser.py  # Jupyter notebook processing
│   ├── python_analyzer.py  # Python code analysis
│   └── config_parser.py    # Configuration file parsing
├── api/                    # Web API
│   └── server.py          # HTTP server
├── cli/                    # Command line interface
│   └── main.py            # CLI implementation
├── utils/                  # Utility functions
└── tests/                  # Test suite
```

## Testing

Run the test suite:
```bash
cd tests
bash test.sh  # Output files are saved in stdout/ directory
```

Or run individual feature tests:
```bash
# Test repository cloning
echo '{"url": "https://github.com/octocat/Hello-World", "local_path": "/tmp/test"}' | python3 feature1_clone.py

# Test file scanning
echo '{"local_path": "/tmp/test", "files": {"test.py": "print(\"hello\")"}, "ignore_patterns": []}' | python3 feature2_scan.py
```

## Requirements

- Python 3.8+
- Git command line tool
- Internet access (for cloning remote repositories)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- Report bugs and issues on [GitHub Issues](https://github.com/yourusername/gitingest/issues)
- Documentation: [GitHub Wiki](https://github.com/yourusername/gitingest/wiki)
- Discussions: [GitHub Discussions](https://github.com/yourusername/gitingest/discussions)