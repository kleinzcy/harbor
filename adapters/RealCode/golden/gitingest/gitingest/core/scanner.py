"""
File system scanning module for GitIngest.
Handles recursive directory scanning with intelligent filtering.
"""

import os
import fnmatch
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class FileScanner:
    """Handles file system scanning with filtering options."""
    
    def __init__(self):
        self.scanned_files = []
    
    def scan_directory(
        self,
        local_path: str,
        ignore_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        max_depth: int = -1,
        max_file_size: Optional[int] = None,
        respect_gitignore: bool = True
    ) -> Dict[str, Any]:
        """
        Scan directory and extract file information.
        
        Args:
            local_path: Path to scan
            ignore_patterns: Patterns to exclude
            include_patterns: Patterns to include (if specified, only these are included)
            max_depth: Maximum recursion depth (-1 for unlimited)
            max_file_size: Maximum file size in bytes
            respect_gitignore: Whether to respect .gitignore files
            
        Returns:
            Dictionary with scanning results
        """
        try:
            local_path = os.path.abspath(local_path)
            
            if not os.path.exists(local_path):
                return {
                    "success": False,
                    "error": f"Path does not exist: {local_path}",
                    "files_found": 0,
                    "files": []
                }
            
            # Load gitignore patterns if requested
            gitignore_patterns = []
            if respect_gitignore:
                gitignore_patterns = self._load_gitignore_patterns(local_path)
            
            # Combine ignore patterns
            all_ignore_patterns = (ignore_patterns or []) + gitignore_patterns
            
            # Scan directory
            files = []
            total_size = 0
            
            for root, dirs, filenames in os.walk(local_path):
                # Calculate current depth
                current_depth = root[len(local_path):].count(os.sep)
                if max_depth >= 0 and current_depth > max_depth:
                    del dirs[:]  # Don't recurse deeper
                    continue
                
                # Filter directories based on patterns
                dirs[:] = [
                    d for d in dirs 
                    if not self._matches_patterns(d, all_ignore_patterns, is_dir=True)
                ]
                
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, local_path)
                    
                    # Check if file should be included
                    if self._should_include_file(
                        filename, rel_path, all_ignore_patterns, include_patterns
                    ):
                        file_info = self._get_file_info(file_path, local_path, max_file_size)
                        if file_info:
                            files.append(file_info)
                            total_size += file_info.get("size", 0)
            
            # Analyze file types
            file_types = self._analyze_file_types(files)
            
            return {
                "success": True,
                "local_path": local_path,
                "files_found": len(files),
                "total_size": total_size,
                "file_types": file_types,
                "files": files,
                "contains_python": any(f.get("extension") == ".py" for f in files),
                "contains_text": any(f.get("extension") in [".txt", ".md", ".rst"] for f in files)
            }
            
        except Exception as e:
            error_msg = f"Scan error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "files_found": 0,
                "files": []
            }
    
    def _load_gitignore_patterns(self, start_path: str) -> List[str]:
        """Load .gitignore patterns from directory hierarchy."""
        patterns = []
        current_path = start_path
        
        while current_path and current_path != os.path.dirname(current_path):
            gitignore_path = os.path.join(current_path, ".gitignore")
            if os.path.exists(gitignore_path):
                try:
                    with open(gitignore_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                patterns.append(line)
                except Exception as e:
                    logger.warning(f"Failed to read .gitignore at {gitignore_path}: {str(e)}")
            
            current_path = os.path.dirname(current_path)
        
        return patterns
    
    def _should_include_file(
        self,
        filename: str,
        rel_path: str,
        ignore_patterns: List[str],
        include_patterns: Optional[List[str]] = None
    ) -> bool:
        """Check if a file should be included based on patterns."""
        # First check include patterns (if specified)
        if include_patterns:
            if not any(fnmatch.fnmatch(filename, pattern) or 
                      fnmatch.fnmatch(rel_path, pattern) 
                      for pattern in include_patterns):
                return False
        
        # Then check ignore patterns
        if self._matches_patterns(filename, ignore_patterns) or \
           self._matches_patterns(rel_path, ignore_patterns):
            return False
        
        return True
    
    def _matches_patterns(self, path: str, patterns: List[str], is_dir: bool = False) -> bool:
        """Check if path matches any of the patterns."""
        for pattern in patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                if is_dir and fnmatch.fnmatch(path, pattern.rstrip('/')):
                    return True
            else:
                if fnmatch.fnmatch(path, pattern):
                    return True
        return False
    
    def _get_file_info(
        self, 
        file_path: str, 
        base_path: str,
        max_file_size: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            # Check file size limit
            if max_file_size and file_size > max_file_size:
                return {
                    "path": os.path.relpath(file_path, base_path),
                    "size": file_size,
                    "truncated": True,
                    "extension": os.path.splitext(file_path)[1],
                    "content": f"[File too large: {file_size} bytes, truncated to {max_file_size} bytes]"
                }
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(max_file_size) if max_file_size else f.read()
            except UnicodeDecodeError:
                # Try different encodings
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read(max_file_size) if max_file_size else f.read()
                except:
                    content = f"[Binary file: {file_size} bytes]"
            
            return {
                "path": os.path.relpath(file_path, base_path),
                "size": file_size,
                "truncated": False,
                "extension": os.path.splitext(file_path)[1],
                "content": content
            }
            
        except Exception as e:
            logger.warning(f"Failed to read file {file_path}: {str(e)}")
            return None
    
    def _analyze_file_types(self, files: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze file types in scanned files."""
        file_types = {}
        for file_info in files:
            ext = file_info.get("extension", "").lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            else:
                file_types["no_extension"] = file_types.get("no_extension", 0) + 1
        return file_types


def scan_directory_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan directory based on input data from test cases.
    
    Args:
        input_data: Dictionary with scanning parameters
        
    Returns:
        Dictionary with scanning results
    """
    scanner = FileScanner()
    
    try:
        # For test cases, we need to create test files first
        local_path = input_data.get("local_path", "")
        files_to_create = input_data.get("files", {})
        
        if files_to_create:
            # Create test directory and files
            os.makedirs(local_path, exist_ok=True)
            for filename, content in files_to_create.items():
                file_path = os.path.join(local_path, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        # Scan directory
        result = scanner.scan_directory(
            local_path=local_path,
            ignore_patterns=input_data.get("ignore_patterns"),
            max_file_size=input_data.get("max_file_size")
        )
        
        # Clean up test files if we created them
        if files_to_create and os.path.exists(local_path):
            import shutil
            shutil.rmtree(local_path)
        
        return result
        
    except Exception as e:
        # Clean up on error
        if 'files_to_create' in locals() and files_to_create and os.path.exists(local_path):
            import shutil
            shutil.rmtree(local_path)
        
        return {
            "success": False,
            "error": str(e),
            "files_found": 0,
            "contains_python": False,
            "contains_text": False
        }