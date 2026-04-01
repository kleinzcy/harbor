# -*- coding: utf-8 -*-
"""INI configuration parser library."""

import logging
import re
from collections import OrderedDict
from typing import Any, List, Optional, Tuple

__version__ = "0.8.0"
__project__ = "Inirama"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "BSD"

NS_LOGGER = logging.getLogger("inirama")


class Scanner:
    """Split a code string into tokens."""

    def __init__(self, source: str, ignore: Optional[List[str]] = None, patterns: Optional[List[Tuple[str, str]]] = None):
        self.source = source
        self.ignore = ignore or []
        self.patterns = patterns or []
        self.tokens: List[Tuple[str, str]] = []

    def reset(self, source: str) -> None:
        """Reset scanner with new source."""
        self.source = source
        self.tokens = []

    def scan(self) -> List[Tuple[str, str]]:
        """Scan source and return tokens."""
        self.pre_scan()
        return self.tokens

    def pre_scan(self) -> None:
        """Pre-scan processing."""
        # Basic implementation - split by lines
        for i, line in enumerate(self.source.splitlines(), 1):
            self.tokens.append(("LINE", f"{i}:{line}"))

    def __repr__(self) -> str:
        """Return representation of scanner."""
        return f"Scanner(source={self.source!r}, tokens={len(self.tokens)})"


class INIScanner(Scanner):
    """INI-specific scanner with predefined patterns."""

    def pre_scan(self) -> None:
        """Pre-scan processing for INI files."""
        # Simplified INI parsing
        in_section = False
        current_section = ""

        for i, line in enumerate(self.source.splitlines(), 1):
            line = line.rstrip()

            # Skip empty lines and comments
            if not line or line.startswith(";") or line.startswith("#"):
                continue

            # Section header
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                self.tokens.append(("SECTION", current_section))
                in_section = True
            # Key-value pair
            elif "=" in line and in_section:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                self.tokens.append(("KEY_VALUE", f"{current_section}.{key}={value}"))
            else:
                # Continuation line or invalid
                pass


class Namespace(OrderedDict):
    """Ordered dictionary with attribute access."""

    def __getattr__(self, name: str) -> Any:
        """Get attribute."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self[name] = value

    def __delattr__(self, name: str) -> None:
        """Delete attribute."""
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class Section(OrderedDict):
    """Ordered mapping representing an INI section."""

    def __init__(self, namespace: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.namespace = namespace

    def __setitem__(self, name: str, value: Any) -> None:
        """Set item with validation."""
        # Convert lists to strings
        if isinstance(value, list):
            value = ",".join(str(v) for v in value)
        super().__setitem__(name, value)


class InterpolationSection(Section):
    """Section with interpolation and raw access controls."""

    def get(self, name: str, default: Any = None) -> Any:
        """Get value with interpolation."""
        value = super().get(name, default)
        if isinstance(value, str) and "${" in value:
            value = self.__interpolate__(value)
        return value

    def __interpolate__(self, value: str) -> str:
        """Interpolate variables in value."""
        # Simple interpolation: ${section.key} or ${key}
        pattern = r"\$\{([^}]+)\}"

        def replace(match: re.Match) -> str:
            key = match.group(1)
            # Try to get from current section first, then from any section
            if "." in key:
                section, key_name = key.split(".", 1)
                # For now, just return the key
                return f"${{{key}}}"
            else:
                return str(self.get(key, f"${{{key}}}"))

        return re.sub(pattern, replace, value)

    def __getitem__(self, name: str, raw: bool = False) -> Any:
        """Get item, optionally without interpolation."""
        value = super().__getitem__(name)
        if raw or not isinstance(value, str):
            return value
        return self.__interpolate__(value)

    def iteritems(self, raw: bool = False) -> List[Tuple[str, Any]]:
        """Iterate over items."""
        items = []
        for key, value in super().items():
            if not raw and isinstance(value, str) and "${" in value:
                value = self.__interpolate__(value)
            items.append((key, value))
        return items


class InterpolationNamespace(Namespace):
    """Namespace that enables interpolation by using InterpolationSection."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        # Use InterpolationSection for all sections
        self.section_class = InterpolationSection

    def add_section(self, name: str) -> InterpolationSection:
        """Add a new section."""
        section = self.section_class(namespace=name)
        self[name] = section
        return section

    def get_section(self, name: str, create: bool = False) -> Optional[InterpolationSection]:
        """Get section by name."""
        if name in self:
            return self[name]
        elif create:
            return self.add_section(name)
        return None


# For backward compatibility
def load_ini(filepath: str) -> InterpolationNamespace:
    """Load INI file into namespace."""
    import configparser

    config = configparser.ConfigParser()
    config.read(filepath)

    namespace = InterpolationNamespace()
    for section in config.sections():
        ns_section = namespace.add_section(section)
        for key, value in config.items(section):
            ns_section[key] = value

    return namespace