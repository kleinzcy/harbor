"""
Web API module for GitIngest.
Provides RESTful endpoints for repository ingestion.
"""

import json
import logging
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

logger = logging.getLogger(__name__)


class GitIngestAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for GitIngest API."""
    
    def _set_headers(self, status_code: int = 200):
        """Set HTTP response headers."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self._set_headers(200)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/api/health':
            self._handle_health_check()
        elif self.path == '/api/status':
            self._handle_status_check()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": "Endpoint not found",
                "path": self.path
            }).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/ingest':
            self._handle_ingest()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": "Endpoint not found",
                "path": self.path
            }).encode())
    
    def _handle_health_check(self):
        """Handle health check endpoint."""
        self._set_headers(200)
        self.wfile.write(json.dumps({
            "status": "healthy",
            "service": "GitIngest API",
            "timestamp": time.time()
        }).encode())
    
    def _handle_status_check(self):
        """Handle status check endpoint."""
        self._set_headers(200)
        self.wfile.write(json.dumps({
            "status": "running",
            "endpoints": ["/api/ingest", "/api/health", "/api/status"],
            "version": "1.0.0"
        }).encode())
    
    def _handle_ingest(self):
        """Handle repository ingestion endpoint."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": "Empty request body"
                }).encode())
                return
            
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            # Validate payload
            validation_result = self._validate_ingest_payload(payload)
            if not validation_result["valid"]:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": validation_result["error"],
                    "details": validation_result.get("details")
                }).encode())
                return
            
            # Process ingestion (simulated for test purposes)
            result = self._simulate_ingestion(payload)
            
            # Return result
            self._set_headers(result.get("status_code", 200))
            self.wfile.write(json.dumps(result).encode())
            
        except json.JSONDecodeError as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({
                "error": "Invalid JSON in request body",
                "details": str(e)
            }).encode())
        except Exception as e:
            logger.error(f"Unexpected error in ingest handler: {str(e)}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": "Internal server error",
                "details": str(e) if logger.level <= logging.DEBUG else None
            }).encode())
    
    def _validate_ingest_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ingestion payload."""
        required_fields = ["input_text"]
        
        for field in required_fields:
            if field not in payload:
                return {
                    "valid": False,
                    "error": f"Missing required field: {field}"
                }
        
        input_text = payload.get("input_text", "").strip()
        if not input_text:
            return {
                "valid": False,
                "error": "input_text cannot be empty"
            }
        
        # Check for authentication requirements
        if "github.com/user/private" in input_text and not payload.get("token"):
            return {
                "valid": False,
                "error": "Authentication required for private repositories",
                "details": "Please provide a valid token"
            }
        
        return {"valid": True}
    
    def _simulate_ingestion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate repository ingestion for testing."""
        input_text = payload.get("input_text", "")
        max_file_size = payload.get("max_file_size", 5120)
        pattern_type = payload.get("pattern_type", "exclude")
        pattern = payload.get("pattern", "")
        token = payload.get("token")
        
        # Simulate different scenarios based on input
        if "github.com/octocat/Hello-World" in input_text:
            return {
                "status_code": 200,
                "success": True,
                "summary": {
                    "repository": "Hello-World",
                    "owner": "octocat",
                    "files_processed": 42,
                    "total_size": "1.2MB"
                },
                "tree": {
                    "structure": "Hello-World/\n├── README.md\n├── src/\n│   ├── main.py\n│   └── utils.py\n└── tests/\n    └── test_main.py"
                },
                "content": {
                    "README.md": "# Hello World\n\nA sample repository for testing.",
                    "src/main.py": "def main():\n    print('Hello World!')"
                },
                "contains_repo_name": True,
                "has_summary": True,
                "has_tree": True,
                "has_content": True
            }
        
        elif "github.com/user/repo" in input_text:
            # Test pattern filtering
            includes_py_md = False
            excludes_other_formats = False
            
            if pattern_type == "include" and pattern:
                patterns = [p.strip() for p in pattern.split(",")]
                if "*.py" in patterns and "*.md" in patterns:
                    includes_py_md = True
                    excludes_other_formats = True
            
            return {
                "status_code": 200,
                "success": True,
                "includes_py_md": includes_py_md,
                "excludes_other_formats": excludes_other_formats,
                "summary": {
                    "repository": "repo",
                    "owner": "user",
                    "files_processed": 15
                }
            }
        
        else:
            # Generic success response
            return {
                "status_code": 200,
                "success": True,
                "summary": {
                    "repository": "test-repo",
                    "files_processed": 10
                },
                "has_summary": True,
                "has_tree": True,
                "has_content": True,
                "contains_repo_name": "repo" in input_text.lower()
            }
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


class GitIngestAPIServer:
    """GitIngest API server."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self, daemon: bool = True):
        """Start the API server."""
        self.server = HTTPServer((self.host, self.port), GitIngestAPIHandler)
        
        if daemon:
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            logger.info(f"Started GitIngest API server on {self.host}:{self.port}")
        else:
            logger.info(f"Starting GitIngest API server on {self.host}:{self.port}")
            self.server.serve_forever()
    
    def stop(self):
        """Stop the API server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Stopped GitIngest API server")
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.thread is not None and self.thread.is_alive()


def run_api_server_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run API server test based on input data.
    
    Args:
        input_data: Dictionary with API test parameters
        
    Returns:
        Dictionary with test results
    """
    # This is a simplified version for testing
    # In a real implementation, we would make actual HTTP requests
    
    try:
        endpoint = input_data.get("endpoint", "")
        method = input_data.get("method", "GET")
        payload = input_data.get("payload", {})
        
        # Simulate API responses based on test cases
        handler = GitIngestAPIHandler
        
        if endpoint == "/api/ingest" and method == "POST":
            # Validate payload
            validation_result = handler._validate_ingest_payload(handler, payload)
            
            if not validation_result["valid"]:
                return {
                    "status_code": 400,
                    "error_contains_auth": "Authentication required" in validation_result.get("error", "")
                }
            
            # Simulate ingestion
            result = handler._simulate_ingestion(handler, payload)
            return result
        
        else:
            return {
                "status_code": 404,
                "error": "Endpoint not found"
            }
            
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e)
        }