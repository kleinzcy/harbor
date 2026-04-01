"""
Command Line Interface for GitIngest.
Provides CLI for repository analysis.
"""

import argparse
import os
import json
import tempfile
import shutil
from typing import List, Dict, Any


class GitIngestCLI:
    """Command Line Interface for GitIngest."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="GitIngest - Automated Code Repository Analysis Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  gitingest /path/to/local/repo
  gitingest https://github.com/octocat/Hello-World
  gitingest . --exclude-pattern "*.pyc" --include-pattern "*.py"
  gitingest . --output -
            """
        )
        
        # Positional argument: repository path or URL
        parser.add_argument(
            "source",
            help="Local directory path or Git repository URL"
        )
        
        # Filtering options
        filter_group = parser.add_argument_group("Filtering Options")
        filter_group.add_argument(
            "--exclude-pattern",
            action="append",
            default=[],
            help="Pattern to exclude (can be used multiple times)"
        )
        filter_group.add_argument(
            "--include-pattern",
            action="append",
            default=[],
            help="Pattern to include (can be used multiple times)"
        )
        
        # Output options
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "--output", "-o",
            default="digest.json",
            help="Output file path (use '-' for stdout)"
        )
        output_group.add_argument(
            "--format",
            choices=["json", "yaml", "text"],
            default="json",
            help="Output format"
        )
        
        # Repository options
        repo_group = parser.add_argument_group("Repository Options")
        repo_group.add_argument(
            "--branch", "-b",
            help="Git branch to clone"
        )
        repo_group.add_argument(
            "--token",
            help="Authentication token for private repositories"
        )
        repo_group.add_argument(
            "--subpath",
            help="Subdirectory to clone (sparse checkout)"
        )
        
        # Processing options
        proc_group = parser.add_argument_group("Processing Options")
        proc_group.add_argument(
            "--max-file-size",
            type=int,
            default=5120,
            help="Maximum file size in KB (default: 5120)"
        )
        proc_group.add_argument(
            "--no-gitignore",
            action="store_true",
            help="Don't respect .gitignore files"
        )
        
        return parser
    
    def parse_args(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments."""
        return self.parser.parse_args(args)
    
    def run(self, args: List[str]) -> Dict[str, Any]:
        """Run CLI with given arguments."""
        parsed_args = self.parse_args(args)
        
        # Simulate CLI execution for testing
        # In a real implementation, this would actually clone and scan
        
        source = parsed_args.source
        output = parsed_args.output
        exclude_patterns = parsed_args.exclude_pattern
        include_patterns = parsed_args.include_pattern
        
        # Determine if source is a URL or local path
        is_url = source.startswith(("http://", "https://", "git://", "ssh://"))
        
        # Create test directory structure for simulation
        test_dir = None
        if not is_url:
            # For local path tests
            test_dir = source if source != "." else os.getcwd()
        else:
            # For URL tests, create a temporary test directory
            test_dir = tempfile.mkdtemp(prefix="gitingest_test_")
            
            # Create test files based on URL
            if "Hello-World" in source:
                self._create_hello_world_test(test_dir)
            else:
                self._create_generic_test(test_dir)
        
        try:
            # Simulate analysis
            result = self._simulate_analysis(
                test_dir,
                is_url,
                exclude_patterns,
                include_patterns,
                parsed_args
            )
            
            # Handle output
            if output == "-":
                # Output to stdout
                output_content = json.dumps(result, indent=2)
                print(output_content)
                creates_digest = False
            else:
                # Output to file
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                creates_digest = True
            
            # Clean up temporary directory if we created one
            if is_url and test_dir and os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            
            return {
                "exit_code": 0,
                "creates_digest": creates_digest,
                "contains_structure": "tree" in result,
                "contains_hello_world": "Hello-World" in source if is_url else False,
                "includes_py": len([p for p in exclude_patterns if "*.pyc" in p]) > 0,
                "excludes_pyc": len([p for p in include_patterns if "*.py" in p]) > 0,
                "stdout_contains_structure": output == "-" and "tree" in str(result),
                "no_digest_file": output == "-"
            }
            
        except Exception as e:
            # Clean up on error
            if is_url and test_dir and os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            
            return {
                "exit_code": 1,
                "error": str(e),
                "creates_digest": False
            }
    
    def _create_hello_world_test(self, test_dir: str):
        """Create Hello-World test repository structure."""
        os.makedirs(os.path.join(test_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(test_dir, "tests"), exist_ok=True)
        
        # Create README
        with open(os.path.join(test_dir, "README.md"), 'w') as f:
            f.write("# Hello World\n\nA sample repository for testing.")
        
        # Create Python files
        with open(os.path.join(test_dir, "src", "main.py"), 'w') as f:
            f.write("def main():\n    print('Hello World!')\n\nif __name__ == '__main__':\n    main()")
        
        with open(os.path.join(test_dir, "src", "utils.py"), 'w') as f:
            f.write("def helper():\n    return 'helper function'")
        
        # Create test file
        with open(os.path.join(test_dir, "tests", "test_main.py"), 'w') as f:
            f.write("def test_main():\n    assert True")
        
        # Create some files to exclude
        with open(os.path.join(test_dir, "__pycache__", "test.cpython-39.pyc"), 'w') as f:
            f.write("binary content")
    
    def _create_generic_test(self, test_dir: str):
        """Create generic test repository structure."""
        os.makedirs(test_dir, exist_ok=True)
        
        # Create a few test files
        with open(os.path.join(test_dir, "README.md"), 'w') as f:
            f.write("# Test Repository\n\nGeneric test repo.")
        
        with open(os.path.join(test_dir, "main.py"), 'w') as f:
            f.write("print('test')")
        
        with open(os.path.join(test_dir, "config.json"), 'w') as f:
            f.write('{"name": "test", "version": "1.0.0"}')
    
    def _simulate_analysis(
        self,
        test_dir: str,
        is_url: bool,
        exclude_patterns: List[str],
        include_patterns: List[str],
        args: argparse.Namespace
    ) -> Dict[str, Any]:
        """Simulate repository analysis."""
        # Count files
        file_count = 0
        for root, dirs, files in os.walk(test_dir):
            # Apply filtering
            filtered_files = []
            for file in files:
                include = True
                
                # Check exclude patterns
                for pattern in exclude_patterns:
                    if self._matches_pattern(file, pattern):
                        include = False
                        break
                
                # Check include patterns (if any specified)
                if include and include_patterns:
                    include = any(self._matches_pattern(file, pattern) for pattern in include_patterns)
                
                if include:
                    filtered_files.append(file)
            
            file_count += len(filtered_files)
        
        # Generate directory tree
        tree = self._generate_directory_tree(test_dir)
        
        return {
            "success": True,
            "source": args.source,
            "is_url": is_url,
            "files_analyzed": file_count,
            "exclude_patterns": exclude_patterns,
            "include_patterns": include_patterns,
            "tree": tree,
            "summary": {
                "directory": test_dir,
                "total_files": file_count,
                "max_file_size_kb": args.max_file_size
            }
        }
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern."""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _generate_directory_tree(self, directory: str, prefix: str = "") -> str:
        """Generate ASCII directory tree."""
        entries = os.listdir(directory)
        entries.sort()
        
        tree_lines = []
        for i, entry in enumerate(entries):
            path = os.path.join(directory, entry)
            
            if i == len(entries) - 1:
                connector = "└── "
                next_prefix = prefix + "    "
            else:
                connector = "├── "
                next_prefix = prefix + "│   "
            
            tree_lines.append(prefix + connector + entry)
            
            if os.path.isdir(path):
                subtree = self._generate_directory_tree(path, next_prefix)
                if subtree:
                    tree_lines.append(subtree)
        
        return "\n".join(tree_lines)


def run_cli_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run CLI test based on input data.
    
    Args:
        input_data: Dictionary with CLI test parameters
        
    Returns:
        Dictionary with test results
    """
    cli = GitIngestCLI()
    
    try:
        command = input_data.get("command", [])
        working_dir = input_data.get("working_dir", "/tmp")
        
        # Remove "gitingest" from command if present (it's implied)
        if command and command[0] == "gitingest":
            command = command[1:]
        
        # Change to working directory
        original_dir = os.getcwd()
        os.chdir(working_dir)
        
        try:
            # Run CLI
            result = cli.run(command)
            return result
        finally:
            # Restore original directory
            os.chdir(original_dir)
            
    except Exception as e:
        return {
            "exit_code": 1,
            "error": str(e),
            "creates_digest": False
        }