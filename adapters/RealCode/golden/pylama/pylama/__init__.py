# -*- coding: utf-8 -*-
"""Pylama - Code audit tool for Python."""

import logging

__version__ = "8.4.2"
__author__ = "Pylama Developers"
__license__ = "MIT"

# Setup logger
LOGGER = logging.getLogger("pylama")
LOGGER.addHandler(logging.NullHandler())

# Core imports for public API
from pylama.core import run
from pylama.main import shell, check_paths, parse_options
from pylama.check_async import check_async
from pylama.errors import Error, remove_duplicates
from pylama.hook import git_hook
from pylama.lint import LINTERS
from pylama.config import DEFAULT_SECTION, get_config
from pylama.libs import inirama
from pylama.config_toml import config_toml

# Import linters to register them
try:
    from pylama.lint import pycodestyle
except ImportError:
    pass

try:
    from pylama.lint import pyflakes
except ImportError:
    pass

try:
    from pylama.lint import mccabe
except ImportError:
    pass

try:
    from pylama.lint import pydocstyle
except ImportError:
    pass

try:
    from pylama.lint import pylint
except ImportError:
    pass

try:
    from pylama.lint import mypy
except ImportError:
    pass

try:
    from pylama.lint import isort
except ImportError:
    pass

try:
    from pylama.lint import eradicate
except ImportError:
    pass

try:
    from pylama.lint import vulture
except ImportError:
    pass

try:
    from pylama.lint import radon
except ImportError:
    pass

# Public API
__all__ = [
    # Core functions
    "run",
    "shell",
    "check_paths",
    "parse_options",
    "check_async",
    "git_hook",
    # Classes
    "Error",
    # Functions
    "remove_duplicates",
    "get_config",
    # Constants
    "DEFAULT_SECTION",
    "LINTERS",
    "LOGGER",
    # Modules
    "inirama",
    "config_toml",
]