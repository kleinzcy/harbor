#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Pylama."""

from pathlib import Path
from setuptools import setup, find_packages

# Read version from pylama/__init__.py
def get_version():
    """Read version from pylama/__init__.py."""
    version_file = Path(__file__).parent / "pylama" / "__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    return "0.0.0"

# Read long description from README.rst
def get_long_description():
    """Read long description from README.rst."""
    readme_file = Path(__file__).parent / "README.rst"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Core dependencies
install_requires = [
    "pycodestyle>=2.9.1",      # PEP8 code style checker
    "pyflakes>=2.5.0",         # Static code analysis tool
    "mccabe>=0.7.0",           # Code complexity calculation tool
    "pydocstyle>=6.1.1",       # Docstring specification checker
    "inirama>=0.3.1",          # INI configuration file parser
    "tomli>=1.2.0; python_version < '3.11'",  # TOML parser for older Python
]

# Optional dependencies for extended functionality
extras_require = {
    "full": [
        "pylint>=2.12.0",      # Comprehensive static code analysis
        "mypy>=0.910",         # Static type checker
        "isort>=5.10.0",       # Import statement sorting checker
        "eradicate>=2.0.0",    # Dead code detector
        "vulture>=2.3",        # Unused code detector
        "radon>=5.1.0",        # Code metric tool
    ],
    "test": [
        "pytest>=7.1.2",
        "pytest-mypy",
        "eradicate>=2.0.0",
        "radon>=5.1.0",
        "mypy",
        "pylint>=2.11.1",
        "pylama-quotes",
        "toml",
        "vulture",
        "types-setuptools",
        "types-toml",
    ],
    "docs": [
        "sphinx>=4.0.0",
        "sphinx-rtd-theme>=1.0.0",
    ],
}

# Entry points
entry_points = {
    "console_scripts": [
        "pylama = pylama.main:shell",
    ],
    "pytest11": [
        "pylama = pylama.pytest",
    ],
}

setup(
    name="pylama",
    version=get_version(),
    description="Code audit tool for Python",
    long_description=get_long_description(),
    long_description_content_type="text/x-rst",
    author="Pylama Developers",
    author_email="pylama@example.com",
    url="https://github.com/klen/pylama",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points=entry_points,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords="code audit, linter, pep8, pyflakes, mccabe, pylint, code quality",
)