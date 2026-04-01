# -*- coding: utf-8 -*-
"""Command-line entry point for python -m pylama."""

import sys

from pylama.main import main

if __name__ == "__main__":
    sys.exit(main())