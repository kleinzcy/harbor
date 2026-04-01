# -*- coding: utf-8 -*-
"""Configuration management for Pylama."""

import logging
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List, Optional

from pylama.libs import inirama

# Constants
DEFAULT_SECTION = "pylama"
DEFAULT_LINTERS = ("pycodestyle", "pyflakes", "mccabe")
CURDIR = Path.cwd()
HOMECFG = Path.home() / ".pylama.ini"
STREAM = logging.StreamHandler(sys.stdout)

# Logger
LOGGER = logging.getLogger("pylama")


class _Default:
    """Wrapper for default configuration values."""

    def __init__(self, value: Any = None):
        self.value = value

    def __str__(self) -> str:
        return str(self.value) if self.value is not None else ""

    def __repr__(self) -> str:
        return f"_Default({self.value!r})"


def get_default_config_file(rootdir: Optional[Path] = None) -> Optional[Path]:
    """Get the default configuration file path.

    Search order:
    1. pylama.ini in current directory or parent directories
    2. setup.cfg in current directory or parent directories
    3. pyproject.toml in current directory or parent directories
    4. ~/.pylama.ini

    :param rootdir: Root directory to start search from
    :return: Path to configuration file or None if not found
    """
    if rootdir is None:
        rootdir = CURDIR

    # Search up the directory tree
    current = rootdir
    while current.parent != current:
        for filename in ["pylama.ini", "setup.cfg", "pyproject.toml"]:
            config_file = current / filename
            if config_file.exists():
                return config_file
        current = current.parent

    # Check home directory
    if HOMECFG.exists():
        return HOMECFG

    return None


def get_config(user_path: Optional[str] = None, rootdir: Optional[Path] = None) -> inirama.Namespace:
    """Load configuration from configuration file.

    :param user_path: The path to the configuration file specified by the user.
    :param rootdir: The root directory, used for parsing relative paths.
    :return: A namespace object containing configuration information.
    """
    if rootdir is None:
        rootdir = CURDIR

    # Determine which config file to use
    config_file: Optional[Path] = None

    if user_path:
        config_file = Path(user_path)
        if not config_file.is_absolute():
            config_file = rootdir / config_file
    else:
        config_file = get_default_config_file(rootdir)

    namespace = inirama.InterpolationNamespace()

    if config_file and config_file.exists():
        if config_file.suffix == ".ini":
            # Load INI file
            namespace = inirama.load_ini(str(config_file))
        elif config_file.name == "setup.cfg":
            # Load setup.cfg as INI
            namespace = inirama.load_ini(str(config_file))
        elif config_file.name == "pyproject.toml":
            # Load TOML file
            from pylama.config_toml import load_toml
            namespace = load_toml(config_file)
        else:
            LOGGER.warning("Unsupported configuration file format: %s", config_file)

    return namespace


def parse_options(
    args: Optional[List[str]] = None,
    config: bool = True,
    rootdir: Optional[Path] = None,
    **overrides: Any,
) -> Namespace:
    """Parse command-line arguments and configuration files to generate unified options.

    :param args: A list of command-line arguments, using `sys.argv` by default.
    :param config: Whether to load the configuration file, default is `True`.
    :param rootdir: The root directory for searching configuration files.
    :param **overrides: Key-value pairs for overriding specific configuration options.
    :return: A `Namespace` object containing all configuration options.
    """
    from pylama.main import setup_parser

    if rootdir is None:
        rootdir = CURDIR

    # Setup parser
    parser = setup_parser()

    # Parse command line arguments
    if args is None:
        args = sys.argv[1:]

    cli_options = parser.parse_args(args)

    # Load configuration if requested
    config_options = Namespace()
    if config:
        config_ns = get_config(None, rootdir)
        # Convert config namespace to argparse namespace
        # This is simplified - actual implementation would map sections
        if DEFAULT_SECTION in config_ns:
            section = config_ns[DEFAULT_SECTION]
            for key, value in section.items():
                setattr(config_options, key, value)

    # Merge options: CLI overrides config
    result = Namespace()

    # Start with defaults
    default_options = get_default_options()
    for key, value in default_options.items():
        setattr(result, key, value)

    # Apply config options
    for key in dir(config_options):
        if not key.startswith("_"):
            value = getattr(config_options, key)
            if value is not None:
                setattr(result, key, value)

    # Apply CLI options
    for key in dir(cli_options):
        if not key.startswith("_"):
            value = getattr(cli_options, key)
            if value is not None and value != parser.get_default(key):
                setattr(result, key, value)

    # Apply overrides
    for key, value in overrides.items():
        setattr(result, key, value)

    return result


def get_default_options() -> Dict[str, Any]:
    """Get default configuration options."""
    return {
        "linters": list(DEFAULT_LINTERS),
        "paths": [CURDIR.as_posix()],
        "ignore": [],
        "select": [],
        "skip": [],
        "format": "pycodestyle",
        "verbose": False,
        "abspath": False,
        "sort": "F,E,W,C,D",
        "concurrent": False,
        "max_line_length": 79,
        "max_complexity": 10,
        "async": False,  # Legacy alias for concurrent
    }


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    LOGGER.handlers = []
    LOGGER.addHandler(STREAM)

    if verbose:
        LOGGER.setLevel(logging.DEBUG)
        STREAM.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.WARNING)
        STREAM.setLevel(logging.WARNING)

    # Format
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    STREAM.setFormatter(formatter)