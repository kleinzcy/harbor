# -*- coding: utf-8 -*-
"""TOML configuration parser for Pylama."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from pylama.libs import InterpolationNamespace

LOGGER = logging.getLogger("pylama")

# Try to import tomli/tomllib
try:
    # Python 3.11+ has tomllib in standard library
    import tomllib
    HAS_TOML = True
except ImportError:
    try:
        # Fall back to tomli
        import tomli as tomllib
        HAS_TOML = True
    except ImportError:
        HAS_TOML = False


def load_toml(filepath: Path) -> InterpolationNamespace:
    """Load TOML configuration file.

    Args:
        filepath: Path to TOML file

    Returns:
        InterpolationNamespace: Configuration namespace

    Raises:
        ImportError: If tomli/tomllib is not available
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not valid TOML
    """
    if not HAS_TOML:
        raise ImportError(
            "TOML support requires tomli/tomllib. "
            "Install with: pip install tomli"
        )

    if not filepath.exists():
        raise FileNotFoundError(f"TOML file not found: {filepath}")

    # Read and parse TOML
    content = filepath.read_text(encoding="utf-8")
    try:
        data = tomllib.loads(content)
    except Exception as e:
        raise ValueError(f"Invalid TOML file {filepath}: {e}") from e

    # Convert to InterpolationNamespace
    namespace = InterpolationNamespace()

    # Look for pylama section
    if "tool" in data and "pylama" in data["tool"]:
        pylama_section = data["tool"]["pylama"]
        _add_section_to_namespace(namespace, "pylama", pylama_section)

    # Also check for top-level pylama section (legacy)
    if "pylama" in data:
        pylama_section = data["pylama"]
        _add_section_to_namespace(namespace, "pylama", pylama_section)

    # Look for linter-specific sections
    _extract_linter_sections(data, namespace)

    return namespace


def _add_section_to_namespace(
    namespace: InterpolationNamespace,
    section_name: str,
    section_data: Dict[str, Any],
) -> None:
    """Add TOML section data to namespace.

    Args:
        namespace: Namespace to add to
        section_name: Name of section
        section_data: Section data from TOML
    """
    section = namespace.add_section(section_name)

    for key, value in section_data.items():
        if isinstance(value, (list, tuple)):
            # Convert lists to comma-separated strings (consistent with INI format)
            section[key] = ",".join(str(v) for v in value)
        else:
            section[key] = str(value)


def _extract_linter_sections(
    data: Dict[str, Any],
    namespace: InterpolationNamespace,
) -> None:
    """Extract linter-specific sections from TOML data.

    Args:
        data: Parsed TOML data
        namespace: Namespace to add sections to
    """
    # Check tool.pylama.linters.*
    if "tool" in data and "pylama" in data["tool"]:
        pylama_data = data["tool"]["pylama"]
        if "linters" in pylama_data:
            linters_data = pylama_data["linters"]
            if isinstance(linters_data, dict):
                for linter_name, linter_config in linters_data.items():
                    if isinstance(linter_config, dict):
                        section_name = f"pylama:{linter_name}"
                        _add_section_to_namespace(namespace, section_name, linter_config)

    # Check top-level linters (legacy)
    if "linters" in data:
        linters_data = data["linters"]
        if isinstance(linters_data, dict):
            for linter_name, linter_config in linters_data.items():
                if isinstance(linter_config, dict):
                    section_name = f"pylama:{linter_name}"
                    _add_section_to_namespace(namespace, section_name, linter_config)


def config_toml(filepath: Optional[Path] = None) -> Optional[InterpolationNamespace]:
    """Convenience function to load TOML config.

    Args:
        filepath: Path to TOML file (default: search for pyproject.toml)

    Returns:
        Optional[InterpolationNamespace]: Configuration namespace or None
    """
    if filepath is None:
        # Search for pyproject.toml in current and parent directories
        current = Path.cwd()
        while current.parent != current:
            toml_file = current / "pyproject.toml"
            if toml_file.exists():
                filepath = toml_file
                break
            current = current.parent

        if filepath is None:
            return None

    try:
        return load_toml(filepath)
    except Exception as e:
        LOGGER.warning("Failed to load TOML config %s: %s", filepath, e)
        return None