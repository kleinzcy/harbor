"""
Python code analysis module for GitIngest.
Extracts imports, functions, and classes from Python code.
"""

import ast
import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)


class PythonCodeAnalyzer:
    """Analyzes Python code to extract structural information."""
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code and extract imports, functions, and classes.
        
        Args:
            code: Python source code
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Extract information
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            docstrings = self._extract_docstrings(tree)
            
            # Check for specific patterns
            has_docstring = len(docstrings) > 0
            has_print = "print" in code
            
            return {
                "success": True,
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "docstrings": docstrings,
                "has_docstring": has_docstring,
                "has_print": has_print,
                "total_elements": len(imports) + len(functions) + len(classes)
            }
            
        except SyntaxError as e:
            error_msg = f"Syntax error in Python code: {str(e)}"
            logger.warning(error_msg)
            
            # Fallback to regex-based extraction for malformed code
            return self._analyze_with_regex(code)
            
        except Exception as e:
            error_msg = f"Code analysis error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "imports": [],
                "functions": [],
                "classes": [],
                "has_docstring": False,
                "has_print": False
            }
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if module:
                        imports.append(f"{module}.{alias.name}")
                    else:
                        imports.append(alias.name)
        
        return imports
    
    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """Extract function definitions from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """Extract class definitions from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes
    
    def _extract_docstrings(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract docstrings from AST."""
        docstrings = []
        
        for node in ast.walk(tree):
            try:
                docstring = ast.get_docstring(node)
                if docstring:
                    if isinstance(node, ast.Module):
                        docstrings.append({"type": "module", "docstring": docstring})
                    elif isinstance(node, ast.FunctionDef):
                        docstrings.append({"type": "function", "name": node.name, "docstring": docstring})
                    elif isinstance(node, ast.ClassDef):
                        docstrings.append({"type": "class", "name": node.name, "docstring": docstring})
            except (AttributeError, TypeError):
                # Some nodes can't have docstrings, skip them
                continue
        
        return docstrings
    
    def _analyze_with_regex(self, code: str) -> Dict[str, Any]:
        """Fallback analysis using regex for malformed code."""
        imports = []
        functions = []
        classes = []
        
        # Extract imports using regex
        import_pattern = r'^\s*import\s+(\w+)|\s*from\s+(\w+)\s+import'
        for match in re.finditer(import_pattern, code, re.MULTILINE):
            if match.group(1):
                imports.append(match.group(1))
            elif match.group(2):
                imports.append(match.group(2))
        
        # Extract functions using regex
        function_pattern = r'^\s*def\s+(\w+)\s*\('
        for match in re.finditer(function_pattern, code, re.MULTILINE):
            functions.append(match.group(1))
        
        # Extract classes using regex
        class_pattern = r'^\s*class\s+(\w+)'
        for match in re.finditer(class_pattern, code, re.MULTILINE):
            classes.append(match.group(1))
        
        # Check for docstrings
        has_docstring = '"""' in code or "'''" in code
        
        return {
            "success": True,
            "imports": imports,
            "functions": functions,
            "classes": classes,
            "has_docstring": has_docstring,
            "has_print": "print" in code,
            "regex_fallback": True
        }


def analyze_python_code_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze Python code based on input data from test cases.
    
    Args:
        input_data: Dictionary with Python code analysis parameters
        
    Returns:
        Dictionary with analysis results
    """
    analyzer = PythonCodeAnalyzer()
    
    try:
        code = input_data.get("code", "")
        
        result = analyzer.analyze_code(code)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "imports": [],
            "functions": [],
            "classes": [],
            "has_docstring": False
        }