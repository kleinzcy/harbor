"""
Utility functions for pysonDB-v2.
"""
import json
import csv
from typing import Dict, Any
from .db_types import DatabaseV2

try:
    import ujson
    JSON_MODULE = ujson
except ImportError:
    JSON_MODULE = json


def migrate(old_db_data: Dict[str, Any]) -> DatabaseV2:
    """
    Convert v1 format ({'data': [{...}]}) to v2 format.

    Args:
        old_db_data: Database in v1 format

    Returns:
        Database in v2 format

    Raises:
        SchemaTypeError: If input data is not valid v1 format
    """
    if not isinstance(old_db_data, dict):
        raise SchemaTypeError("Database must be a dictionary")

    if 'data' not in old_db_data or not isinstance(old_db_data['data'], list):
        raise SchemaTypeError("v1 database must have 'data' key with list value")

    # Extract all keys from all records
    keys_set = set()
    for record in old_db_data['data']:
        if isinstance(record, dict):
            keys_set.update(record.keys())

    # Sort keys alphabetically
    keys = sorted(keys_set)

    # Convert list of records to dict with IDs
    data_dict = {}
    for i, record in enumerate(old_db_data['data']):
        if isinstance(record, dict):
            # Generate ID (v1 used numeric IDs, but we'll keep them as strings)
            record_id = str(i + 1)
            # Sort record keys alphabetically
            sorted_record = {k: record[k] for k in sorted(record.keys())}
            data_dict[record_id] = sorted_record

    return {
        'version': 2,
        'keys': keys,
        'data': data_dict
    }


def merge_n_db(*dbs: DatabaseV2) -> DatabaseV2:
    """
    Merge multiple v2 databases with same schema.

    Args:
        *dbs: Databases to merge

    Returns:
        Merged database

    Raises:
        ValueError: If databases have incompatible schemas
    """
    if not dbs:
        return {'version': 2, 'keys': [], 'data': {}}

    # Check all databases have same keys
    first_keys = set(dbs[0]['keys'])
    for i, db in enumerate(dbs[1:], 1):
        if set(db['keys']) != first_keys:
            raise ValueError(f"Database {i} has incompatible schema")

    # Merge data, ensuring unique IDs
    merged_data = {}
    for db in dbs:
        for record_id, record in db['data'].items():
            # Generate new ID if collision (simple approach: append suffix)
            new_id = record_id
            counter = 1
            while new_id in merged_data:
                new_id = f"{record_id}_{counter}"
                counter += 1
            merged_data[new_id] = record

    return {
        'version': 2,
        'keys': dbs[0]['keys'],
        'data': merged_data
    }


def print_db_as_table(data: DatabaseV2) -> str:
    """
    Format database as pretty table string.

    Args:
        data: Database in v2 format

    Returns:
        Formatted table as string
    """
    try:
        from prettytable import PrettyTable
        use_prettytable = True
    except ImportError:
        use_prettytable = False

    if not data['data']:
        return "No data"

    # Get all keys (including any that might not be in schema)
    all_keys = set(data['keys'])
    for record in data['data'].values():
        all_keys.update(record.keys())

    keys = sorted(all_keys)

    if use_prettytable:
        table = PrettyTable()
        table.field_names = ['ID'] + keys
        for record_id, record in data['data'].items():
            row = [record_id]
            for key in keys:
                row.append(record.get(key, ''))
            table.add_row(row)
        return str(table)
    else:
        # Simple text table
        lines = []
        # Header
        header = 'ID'.ljust(20) + ' | ' + ' | '.join(k.ljust(15) for k in keys)
        lines.append(header)
        lines.append('-' * len(header))

        # Rows
        for record_id, record in data['data'].items():
            row = record_id.ljust(20) + ' | '
            row += ' | '.join(str(record.get(key, '')).ljust(15) for key in keys)
            lines.append(row)

        return '\n'.join(lines)


def purge_db(_: Any = None) -> DatabaseV2:
    """
    Return empty v2 database structure.

    Args:
        _: Ignored parameter (for compatibility)

    Returns:
        Empty v2 database structure
    """
    return {'version': 2, 'keys': [], 'data': {}}


def to_csv(db: DatabaseV2, output_file: str) -> None:
    """
    Export database to CSV file.

    Args:
        db: Database in v2 format
        output_file: Path to output CSV file
    """
    if not db['data']:
        # Create empty CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            pass
        return

    # Get all keys (including any that might not be in schema)
    all_keys = set(db['keys'])
    for record in db['data'].values():
        all_keys.update(record.keys())

    keys = sorted(all_keys)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header row
        writer.writerow(['ID'] + list(keys))

        # Data rows
        for record_id, record in db['data'].items():
            row = [record_id]
            for key in keys:
                row.append(record.get(key, ''))
            writer.writerow(row)