"""
Configuration file parsing module for GitIngest.
Extracts key-value pairs from various config file formats.
"""

import json
import logging
from typing import Dict, Any, List
import configparser

# Try to import yaml, but make it optional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Try to import tomllib (Python 3.11+) or tomli (for older Python)
try:
    import tomllib
    TOML_AVAILABLE = True
except ImportError:
    try:
        import tomli as tomllib
        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConfigFileParser:
    """Parses configuration files in various formats."""
    
    def parse_config(self, content: str, format: str) -> Dict[str, Any]:
        """
        Parse configuration content.
        
        Args:
            content: Configuration file content
            format: Format type (json, yaml, toml, ini)
            
        Returns:
            Dictionary with parsing results
        """
        try:
            format = format.lower()
            
            if format == "json":
                return self._parse_json(content)
            elif format == "yaml":
                return self._parse_yaml(content)
            elif format == "toml":
                return self._parse_toml(content)
            elif format == "ini":
                return self._parse_ini(content)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format}",
                    "keys": [],
                    "values": []
                }
                
        except Exception as e:
            error_msg = f"Config parsing error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "keys": [],
                "values": []
            }
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON configuration."""
        data = json.loads(content)
        keys = list(data.keys())
        values = list(data.values())
        
        return {
            "success": True,
            "format": "json",
            "data": data,
            "keys": keys,
            "values": values,
            "key_count": len(keys)
        }
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """Parse YAML configuration."""
        if not YAML_AVAILABLE:
            return {
                "success": False,
                "error": "YAML parsing requires PyYAML package",
                "format": "yaml",
                "keys": [],
                "values": []
            }
        
        try:
            data = yaml.safe_load(content)
            
            if data is None:
                return {
                    "success": True,
                    "format": "yaml",
                    "data": {},
                    "keys": [],
                    "values": [],
                    "key_count": 0
                }
            
            keys = list(data.keys())
            values = list(data.values())
            
            return {
                "success": True,
                "format": "yaml",
                "data": data,
                "keys": keys,
                "values": values,
                "key_count": len(keys)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"YAML parsing error: {str(e)}",
                "format": "yaml",
                "keys": [],
                "values": []
            }
    
    def _parse_toml(self, content: str) -> Dict[str, Any]:
        """Parse TOML configuration."""
        if not TOML_AVAILABLE:
            return {
                "success": False,
                "error": "TOML parsing requires Python 3.11+ or tomli package",
                "format": "toml",
                "keys": [],
                "values": []
            }
        
        try:
            data = tomllib.loads(content)
            keys = list(data.keys())
            values = list(data.values())
            
            return {
                "success": True,
                "format": "toml",
                "data": data,
                "keys": keys,
                "values": values,
                "key_count": len(keys)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"TOML parsing error: {str(e)}",
                "format": "toml",
                "keys": [],
                "values": []
            }
    
    def _parse_ini(self, content: str) -> Dict[str, Any]:
        """Parse INI configuration."""
        parser = configparser.ConfigParser()
        
        # Use StringIO to simulate file reading
        parser.read_string(content)
        
        data = {}
        keys = []
        values = []
        
        for section in parser.sections():
            section_data = dict(parser.items(section))
            data[section] = section_data
            keys.append(section)
            values.append(section_data)
        
        # Also get default section if it exists
        if parser.defaults():
            data["DEFAULT"] = dict(parser.defaults())
            keys.append("DEFAULT")
            values.append(data["DEFAULT"])
        
        return {
            "success": True,
            "format": "ini",
            "data": data,
            "keys": keys,
            "values": values,
            "key_count": len(keys)
        }
    
    def extract_key_value_pairs(self, data: Any, prefix: str = "") -> List[Dict[str, Any]]:
        """
        Extract all key-value pairs from nested data structure.
        
        Args:
            data: Parsed configuration data
            prefix: Key prefix for nested structures
            
        Returns:
            List of key-value pairs
        """
        pairs = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, (dict, list)):
                    # Recursively process nested structures
                    pairs.extend(self.extract_key_value_pairs(value, full_key))
                else:
                    pairs.append({
                        "key": full_key,
                        "value": value,
                        "type": type(value).__name__
                    })
        
        elif isinstance(data, list):
            for i, value in enumerate(data):
                full_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
                
                if isinstance(value, (dict, list)):
                    pairs.extend(self.extract_key_value_pairs(value, full_key))
                else:
                    pairs.append({
                        "key": full_key,
                        "value": value,
                        "type": type(value).__name__
                    })
        
        return pairs


def parse_config_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse configuration based on input data from test cases.
    
    Args:
        input_data: Dictionary with config parsing parameters
        
    Returns:
        Dictionary with parsing results
    """
    parser = ConfigFileParser()
    
    try:
        format = input_data.get("format", "")
        content = input_data.get("content", "")
        
        result = parser.parse_config(content, format)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "keys": [],
            "values": []
        }