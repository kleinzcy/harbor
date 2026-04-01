"""
Repository cloning module for GitIngest.
Handles cloning from various Git platforms with authentication support.
"""

import os
import shutil
import tempfile
import subprocess
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RepositoryCloner:
    """Handles cloning of Git repositories from various platforms."""
    
    def __init__(self):
        self.temp_dirs = []
    
    def clone_repository(
        self,
        url: str,
        local_path: Optional[str] = None,
        branch: Optional[str] = None,
        token: Optional[str] = None,
        subpath: Optional[str] = None,
        depth: Optional[int] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Clone a Git repository.
        
        Args:
            url: Repository URL
            local_path: Local path to clone to (if None, creates temp directory)
            branch: Specific branch to clone
            token: Authentication token for private repositories
            subpath: Subdirectory to clone (sparse checkout)
            depth: Clone depth (for shallow clones)
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with cloning results
        """
        try:
            # Prepare URL with authentication if token provided
            clone_url = self._prepare_url(url, token)
            
            # Prepare local path
            if local_path is None:
                local_path = tempfile.mkdtemp(prefix="gitingest_")
                self.temp_dirs.append(local_path)
            
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
            
            # Build git clone command
            cmd = ["git", "clone"]
            
            if branch:
                cmd.extend(["--branch", branch])
            
            if depth:
                cmd.extend(["--depth", str(depth)])
            
            if subpath:
                cmd.extend(["--filter=blob:none", "--sparse"])
            
            cmd.extend([clone_url, local_path])
            
            logger.info(f"Cloning repository: {url} to {local_path}")
            
            # Execute clone command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error_msg = f"Clone failed: {result.stderr}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "local_path": local_path,
                    "git_dir_exists": False
                }
            
            # Handle sparse checkout if subpath specified
            if subpath:
                sparse_result = self._setup_sparse_checkout(local_path, subpath)
                if not sparse_result["success"]:
                    return {
                        "success": False,
                        "error": sparse_result["error"],
                        "local_path": local_path,
                        "git_dir_exists": True,
                        "subpath_exists": False
                    }
            
            # Verify clone was successful
            git_dir = os.path.join(local_path, ".git")
            git_dir_exists = os.path.exists(git_dir)
            
            # Check for README file
            readme_exists = self._check_readme_exists(local_path)
            
            # Check if subpath exists if specified
            subpath_exists = True
            if subpath:
                full_subpath = os.path.join(local_path, subpath.lstrip("/"))
                subpath_exists = os.path.exists(full_subpath)
            
            return {
                "success": True,
                "local_path": local_path,
                "git_dir_exists": git_dir_exists,
                "readme_exists": readme_exists,
                "subpath_exists": subpath_exists if subpath else None,
                "branch": branch if branch else "main"
            }
            
        except subprocess.TimeoutExpired:
            error_msg = f"Clone timeout after {timeout} seconds"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "local_path": local_path,
                "git_dir_exists": False
            }
        except Exception as e:
            error_msg = f"Clone error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "local_path": local_path,
                "git_dir_exists": False
            }
    
    def _prepare_url(self, url: str, token: Optional[str] = None) -> str:
        """Prepare URL with authentication token if provided."""
        if not token:
            return url

        parsed = urlparse(url)

        # Don't modify file:// URLs
        if parsed.scheme == "file":
            return url

        # Handle GitHub tokens
        if "github.com" in parsed.netloc:
            return f"https://{token}@{parsed.netloc}{parsed.path}"

        # Handle GitLab tokens
        elif "gitlab.com" in parsed.netloc:
            return f"https://oauth2:{token}@{parsed.netloc}{parsed.path}"

        # Handle Bitbucket tokens
        elif "bitbucket.org" in parsed.netloc:
            return f"https://x-token-auth:{token}@{parsed.netloc}{parsed.path}"

        # Generic token injection for other https URLs
        else:
            # Only inject token if scheme is http or https
            if parsed.scheme in ("http", "https"):
                return f"https://{token}@{parsed.netloc}{parsed.path}"
            else:
                # For other schemes (ssh, git, etc.), return original URL
                return url
    
    def _setup_sparse_checkout(self, repo_path: str, subpath: str) -> Dict[str, Any]:
        """Set up sparse checkout for a specific subdirectory."""
        try:
            # Initialize sparse checkout
            subprocess.run(
                ["git", "sparse-checkout", "init", "--cone"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            # Set sparse checkout directory
            subprocess.run(
                ["git", "sparse-checkout", "set", subpath],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Sparse checkout failed: {str(e)}"
            }
    
    def _check_readme_exists(self, repo_path: str) -> bool:
        """Check if any README file exists in the repository."""
        readme_patterns = [
            "README",
            "README.md",
            "README.txt",
            "README.rst",
            "readme",
            "Readme"
        ]
        
        for pattern in readme_patterns:
            for ext in ["", ".md", ".txt", ".rst", ".adoc"]:
                readme_path = os.path.join(repo_path, f"{pattern}{ext}")
                if os.path.exists(readme_path):
                    return True
        
        return False
    
    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {temp_dir}: {str(e)}")
        self.temp_dirs = []


def clone_repository_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clone repository based on input data from test cases.
    
    Args:
        input_data: Dictionary with cloning parameters
        
    Returns:
        Dictionary with cloning results
    """
    cloner = RepositoryCloner()
    
    try:
        result = cloner.clone_repository(
            url=input_data.get("url", ""),
            local_path=input_data.get("local_path"),
            branch=input_data.get("branch"),
            token=input_data.get("token"),
            subpath=input_data.get("subpath")
        )
        
        # Clean up temporary directories
        cloner.cleanup()
        
        return result
        
    except Exception as e:
        cloner.cleanup()
        return {
            "success": False,
            "error": str(e),
            "git_dir_exists": False,
            "readme_exists": False,
            "subpath_exists": False
        }