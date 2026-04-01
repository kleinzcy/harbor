"""
Jupyter Notebook processing module for GitIngest.
Converts Jupyter notebooks to readable code format.
"""

import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class NotebookProcessor:
    """Handles conversion of Jupyter notebooks to Python code."""
    
    def process_notebook(
        self,
        notebook_data: Dict[str, Any],
        include_output: bool = False
    ) -> Dict[str, Any]:
        """
        Process Jupyter notebook and convert to Python code.
        
        Args:
            notebook_data: Notebook JSON data
            include_output: Whether to include cell outputs
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract cells from notebook
            cells = notebook_data.get("cells", [])
            
            # Process each cell
            python_code = []
            contains_import = False
            contains_print = False
            contains_output = False
            contains_markdown = False
            
            for cell in cells:
                cell_type = cell.get("cell_type", "")
                source = cell.get("source", [])
                outputs = cell.get("outputs", [])
                
                if cell_type == "code":
                    # Add code cell
                    code_content = "".join(source)
                    python_code.append(code_content)
                    
                    # Check for imports and prints
                    if "import" in code_content.lower():
                        contains_import = True
                    if "print" in code_content:
                        contains_print = True
                    
                    # Add outputs if requested
                    if include_output and outputs:
                        output_text = self._extract_output_text(outputs)
                        if output_text:
                            python_code.append(f"# Output: {output_text}")
                            contains_output = True
                    
                elif cell_type == "markdown":
                    # Convert markdown to comments
                    markdown_content = "".join(source)
                    comment_lines = []
                    for line in markdown_content.split('\n'):
                        if line.strip():
                            comment_lines.append(f"# {line}")
                        else:
                            comment_lines.append("#")
                    
                    if comment_lines:
                        python_code.append("\n".join(comment_lines))
                        contains_markdown = True
            
            # Combine all code
            final_code = "\n\n".join(python_code)
            
            return {
                "success": True,
                "code": final_code,
                "contains_import": contains_import,
                "contains_print": contains_print,
                "contains_output": contains_output,
                "contains_markdown": contains_markdown,
                "cell_count": len(cells),
                "code_cells": len([c for c in cells if c.get("cell_type") == "code"]),
                "markdown_cells": len([c for c in cells if c.get("cell_type") == "markdown"])
            }
            
        except Exception as e:
            error_msg = f"Notebook processing error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "contains_import": False,
                "contains_print": False,
                "contains_output": False,
                "contains_markdown": False
            }
    
    def _extract_output_text(self, outputs: List[Dict[str, Any]]) -> str:
        """Extract text from notebook cell outputs."""
        output_texts = []
        
        for output in outputs:
            output_type = output.get("output_type", "")
            
            if output_type == "stream":
                text = output.get("text", "")
                if isinstance(text, list):
                    text = "".join(text)
                output_texts.append(text.strip())
            
            elif output_type == "execute_result":
                data = output.get("data", {})
                if "text/plain" in data:
                    text = data["text/plain"]
                    if isinstance(text, list):
                        text = "".join(text)
                    output_texts.append(text.strip())
            
            elif output_type == "display_data":
                data = output.get("data", {})
                if "text/plain" in data:
                    text = data["text/plain"]
                    if isinstance(text, list):
                        text = "".join(text)
                    output_texts.append(text.strip())
        
        return "\n".join(output_texts)
    
    def process_notebook_file(
        self,
        file_path: str,
        include_output: bool = False
    ) -> Dict[str, Any]:
        """
        Process Jupyter notebook file.
        
        Args:
            file_path: Path to .ipynb file
            include_output: Whether to include cell outputs
            
        Returns:
            Dictionary with processing results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook_data = json.load(f)
            
            return self.process_notebook(notebook_data, include_output)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid notebook JSON: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"File processing error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


def process_notebook_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process notebook based on input data from test cases.
    
    Args:
        input_data: Dictionary with notebook processing parameters
        
    Returns:
        Dictionary with processing results
    """
    processor = NotebookProcessor()
    
    try:
        notebook_data = input_data.get("notebook", {})
        include_output = input_data.get("include_output", False)
        
        result = processor.process_notebook(notebook_data, include_output)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "contains_import": False,
            "contains_print": False,
            "contains_output": False,
            "contains_markdown": False
        }