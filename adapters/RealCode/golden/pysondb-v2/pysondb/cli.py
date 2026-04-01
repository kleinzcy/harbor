"""
Command-line interface for pysonDB-v2.
"""
import argparse
import json
import sys
import os
from .utils import migrate, merge_n_db, print_db_as_table, to_csv

try:
    import ujson
    JSON_MODULE = ujson
except ImportError:
    JSON_MODULE = json


def info_command() -> int:
    """Display version and JSON parser info."""
    print("PysonDB v2.0.0")
    print(f"JSON parser: {JSON_MODULE.__name__}")
    return 0


def migrate_command(args: argparse.Namespace) -> int:
    """Migrate v1 database to v2 format."""
    try:
        with open(args.old_db, 'r', encoding='utf-8') as f:
            old_data = JSON_MODULE.load(f)

        new_data = migrate(old_data)

        with open(args.new_db, 'w', encoding='utf-8') as f:
            JSON_MODULE.dump(new_data, f, indent=args.indent)

        print(f"Successfully migrated {args.old_db} to {args.new_db}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def show_command(args: argparse.Namespace) -> int:
    """Display database as formatted table."""
    try:
        with open(args.db_file, 'r', encoding='utf-8') as f:
            data = JSON_MODULE.load(f)

        if data.get('version') != 2:
            print("Error: Database is not v2 format", file=sys.stderr)
            return 1

        table = print_db_as_table(data)
        print(table)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def merge_command(args: argparse.Namespace) -> int:
    """Merge multiple databases."""
    try:
        databases = []
        for db_file in args.db_files:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = JSON_MODULE.load(f)

            if data.get('version') != 2:
                print(f"Error: {db_file} is not v2 format", file=sys.stderr)
                return 1

            databases.append(data)

        merged = merge_n_db(*databases)

        with open(args.output, 'w', encoding='utf-8') as f:
            JSON_MODULE.dump(merged, f, indent=2)

        print(f"DB's merged successfully into {args.output}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def tocsv_command(args: argparse.Namespace) -> int:
    """Export database to CSV format."""
    try:
        with open(args.db_file, 'r', encoding='utf-8') as f:
            data = JSON_MODULE.load(f)

        if data.get('version') != 2:
            print("Error: Database is not v2 format", file=sys.stderr)
            return 1

        output_file = args.output if args.output else f"{os.path.splitext(args.db_file)[0]}.csv"
        to_csv(data, output_file)

        print(f"Exported to {output_file}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def purge_command(args: argparse.Namespace) -> int:
    """Clear database contents."""
    try:
        with open(args.db_file, 'r', encoding='utf-8') as f:
            data = JSON_MODULE.load(f)

        if data.get('version') != 2:
            print("Error: Database is not v2 format", file=sys.stderr)
            return 1

        data['data'] = {}

        with open(args.db_file, 'w', encoding='utf-8') as f:
            JSON_MODULE.dump(data, f, indent=2)

        print(f"Purged {args.db_file}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="pysonDB-v2 - Lightweight JSON database management"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # info command
    subparsers.add_parser('info', help='Display version and JSON parser info')

    # migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate v1 database to v2 format')
    migrate_parser.add_argument('old_db', help='Path to v1 database file')
    migrate_parser.add_argument('new_db', help='Path to output v2 database file')
    migrate_parser.add_argument('--indent', type=int, default=2, help='JSON indentation level')

    # show command
    show_parser = subparsers.add_parser('show', help='Display database as formatted table')
    show_parser.add_argument('db_file', help='Path to database file')

    # merge command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple databases')
    merge_parser.add_argument('db_files', nargs='+', help='Paths to database files to merge')
    merge_parser.add_argument('--output', required=True, help='Path to output merged database')

    # tocsv command
    tocsv_parser = subparsers.add_parser('tocsv', help='Export database to CSV format')
    tocsv_parser.add_argument('db_file', help='Path to database file')
    tocsv_parser.add_argument('--output', help='Path to output CSV file (default: same name as db with .csv extension)')

    # purge command
    purge_parser = subparsers.add_parser('purge', help='Clear database contents')
    purge_parser.add_argument('db_file', help='Path to database file')

    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Dispatch to command handler
    if args.command == 'info':
        sys.exit(info_command())
    elif args.command == 'migrate':
        sys.exit(migrate_command(args))
    elif args.command == 'show':
        sys.exit(show_command(args))
    elif args.command == 'merge':
        sys.exit(merge_command(args))
    elif args.command == 'tocsv':
        sys.exit(tocsv_command(args))
    elif args.command == 'purge':
        sys.exit(purge_command(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()