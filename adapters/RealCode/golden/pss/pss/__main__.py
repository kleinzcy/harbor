#!/usr/bin/env python3
"""
Command-line entry point for PSS.
"""
import sys

from .cli import parse_args, pss_run


def main() -> int:
    """Main entry point."""
    try:
        args = parse_args()
        return pss_run(args)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())