Pylama
======

Code audit tool for Python.

.. image:: https://img.shields.io/pypi/v/pylama.svg
    :target: https://pypi.python.org/pypi/pylama
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/pylama.svg
    :target: https://pypi.python.org/pypi/pylama
    :alt: Python Versions

.. image:: https://img.shields.io/pypi/l/pylama.svg
    :target: https://pypi.python.org/pypi/pylama
    :alt: License

.. image:: https://github.com/klen/pylama/workflows/Tests/badge.svg
    :target: https://github.com/klen/pylama/actions
    :alt: Build Status

Pylama is a command-line tool for Python code quality auditing that integrates multiple code checkers and static analysis tools to conduct comprehensive quality checks on Python code.

Features
--------

- **Multi-Linter Integration**: Centralized interface for multiple Python code checkers (pycodestyle, pyflakes, mccabe, pydocstyle, pylint, mypy, isort, eradicate, vulture, radon)
- **Unified Configuration**: Support for INI, TOML, setup.cfg, and pyproject.toml configuration files with hierarchical precedence
- **File Scanning**: Recursive directory scanning with pattern matching and ignore rules
- **Error Reporting**: Multiple output formats (pydocstyle, pycodestyle, pylint, parsable, json) with configurable sorting and filtering
- **Asynchronous Processing**: Concurrent checking for large codebases with performance optimization
- **Git Hooks**: Pre-commit hook integration for automated code quality checks
- **Error Deduplication**: Automatic removal of duplicate errors from multiple linters

Installation
------------

.. code-block:: bash

    pip install pylama

For full functionality with all optional linters:

.. code-block:: bash

    pip install pylama[full]

Usage
-----

Basic command line usage:

.. code-block:: bash

    # Check current directory
    pylama

    # Check specific files or directories
    pylama myproject/ tests/

    # Use specific linters
    pylama --linters=pycodestyle,pyflakes myfile.py

    # Output in JSON format
    pylama --format=json myfile.py

    # Check code from stdin
    echo "x=1" | pylama -

Python API:

.. code-block:: python

    from pylama.main import check_paths, parse_options

    # Basic check
    options = parse_options()
    errors = check_paths(["./src"], options)

    for error in errors:
        print(f"{error['filename']}:{error['lnum']}:{error['col']} "
              f"{error['type']} {error['text']}")

Configuration
-------------

Pylama supports multiple configuration file formats:

``pylama.ini`` (INI format):

.. code-block:: ini

    [pylama]
    linters = pycodestyle,pyflakes,mccabe
    ignore = E203,W503
    max_line_length = 100

    [pylama:pycodestyle]
    max_line_length = 120
    ignore = E501

    [pylama:mccabe]
    max_complexity = 15

``pyproject.toml`` (TOML format):

.. code-block:: toml

    [tool.pylama]
    linters = ["pycodestyle", "pyflakes", "mccabe"]
    ignore = ["E203", "W503"]
    max_line_length = 100

    [tool.pylama.linter.pycodestyle]
    max_line_length = 120
    ignore = ["E501"]

    [tool.pylama.linter.mccabe]
    max-complexity = 15

Git Hooks
---------

Install a pre-commit hook:

.. code-block:: bash

    pylama --install-git-hook

Or programmatically:

.. code-block:: python

    from pylama.hook import git_hook
    git_hook(complexity=10, strict=True, linters="pycodestyle,mccabe")

License
-------

MIT License. See LICENSE file for details.