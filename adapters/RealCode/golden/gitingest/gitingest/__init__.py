"""
GitIngest - Automated Code Repository Analysis Tool
"""

__version__ = "1.0.0"
__author__ = "GitIngest Team"
__email__ = "team@gitingest.dev"

# Core modules
from .core.cloner import RepositoryCloner, clone_repository_from_input
from .core.scanner import FileScanner, scan_directory_from_input

# Parser modules
from .parsers.notebook_parser import NotebookProcessor, process_notebook_from_input
from .parsers.python_analyzer import PythonCodeAnalyzer, analyze_python_code_from_input
from .parsers.config_parser import ConfigFileParser, parse_config_from_input

# API module
from .api.server import GitIngestAPIServer, GitIngestAPIHandler, run_api_server_from_input

# CLI module
from .cli.main import GitIngestCLI, run_cli_from_input

__all__ = [
    # Core
    "RepositoryCloner",
    "clone_repository_from_input",
    "FileScanner",
    "scan_directory_from_input",
    
    # Parsers
    "NotebookProcessor",
    "process_notebook_from_input",
    "PythonCodeAnalyzer",
    "analyze_python_code_from_input",
    "ConfigFileParser",
    "parse_config_from_input",
    
    # API
    "GitIngestAPIServer",
    "GitIngestAPIHandler",
    "run_api_server_from_input",
    
    # CLI
    "GitIngestCLI",
    "run_cli_from_input",
]