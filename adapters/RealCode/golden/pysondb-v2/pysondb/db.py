"""
Main database class for pysonDB-v2.
"""
import json
import os
import threading
import uuid
from typing import Any, Dict, List, Iterable
from .errors import IdDoesNotExistError, UnknownKeyError, SchemaTypeError
from .db_types import QueryFunc, IdGenerator

try:
    import ujson
    JSON_MODULE = ujson
except ImportError:
    JSON_MODULE = json


class PysonDB:
    """Main database class providing CRUD operations on JSON files."""

    def __init__(self, filepath: str, auto_dump: bool = True, indent: int = 2):
        """
        Initialize database.

        Args:
            filepath: Path to JSON database file
            auto_dump: Whether to automatically save changes to file
            indent: JSON indentation level (for pretty printing)
        """
        self.filepath = filepath
        self.auto_dump = auto_dump
        self.indent = indent
        self.lock = threading.RLock()
        self._id_generator = self._default_id_generator

        # Load or initialize database
        self._load()

    def _default_id_generator(self) -> str:
        """Default ID generator using UUID."""
        return str(uuid.uuid4().hex)[:18]

    def set_id_generator(self, generator: IdGenerator) -> None:
        """Set custom ID generator function."""
        self._id_generator = generator

    def _load(self) -> None:
        """Load database from file or initialize empty structure."""
        if os.path.exists(self.filepath):
            with self.lock:
                try:
                    with open(self.filepath, 'r', encoding='utf-8') as f:
                        data = JSON_MODULE.load(f)

                    # Validate schema
                    if not isinstance(data, dict):
                        raise SchemaTypeError("Database root must be a dictionary")

                    if data.get('version') != 2:
                        raise SchemaTypeError(f"Unsupported database version: {data.get('version')}")

                    if 'keys' not in data or not isinstance(data['keys'], list):
                        raise SchemaTypeError("Database missing 'keys' list")

                    if 'data' not in data or not isinstance(data['data'], dict):
                        raise SchemaTypeError("Database missing 'data' dictionary")

                    # Ensure keys are sorted alphabetically
                    data['keys'] = sorted(data['keys'])

                    self._data = data
                except (json.JSONDecodeError, ValueError) as e:
                    raise SchemaTypeError(f"Failed to parse database file: {e}")
        else:
            # Initialize empty database
            self._data = {
                'version': 2,
                'keys': [],
                'data': {}
            }
            if self.auto_dump:
                self._dump()

    def _dump(self) -> None:
        """Save database to file."""
        with self.lock:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)

            with open(self.filepath, 'w', encoding='utf-8') as f:
                JSON_MODULE.dump(self._data, f, indent=self.indent)

    def add(self, record: Dict[str, Any]) -> str:
        """
        Add a single record with auto-generated ID.

        Args:
            record: Dictionary containing record data

        Returns:
            Generated ID for the new record

        Raises:
            UnknownKeyError: If record contains unknown fields or misses required fields
            TypeError: If record is not a dictionary
        """
        if not isinstance(record, dict):
            raise TypeError("Record must be a dictionary")

        with self.lock:
            # Validate keys against schema
            self._validate_keys(record.keys())

            # Sort keys alphabetically for consistency
            sorted_record = {k: record[k] for k in sorted(record.keys())}

            # Generate ID
            record_id = self._id_generator()

            # Add to data
            self._data['data'][record_id] = sorted_record

            # Update schema if new keys were added
            self._update_schema(sorted_record.keys())

            if self.auto_dump:
                self._dump()

            return record_id

    def add_many(self, records: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple records in batch.

        Args:
            records: List of dictionaries containing record data

        Returns:
            List of generated IDs for the new records

        Raises:
            UnknownKeyError: If any record contains unknown fields or misses required fields
            TypeError: If records is not a list or contains non-dictionary items
        """
        if not isinstance(records, list):
            raise TypeError("Records must be a list")

        ids = []
        with self.lock:
            for record in records:
                if not isinstance(record, dict):
                    raise TypeError("All records must be dictionaries")

                # Validate keys against schema
                self._validate_keys(record.keys())

                # Sort keys alphabetically
                sorted_record = {k: record[k] for k in sorted(record.keys())}

                # Generate ID
                record_id = self._id_generator()

                # Add to data
                self._data['data'][record_id] = sorted_record

                # Update schema if new keys were added
                self._update_schema(sorted_record.keys())

                ids.append(record_id)

            if self.auto_dump:
                self._dump()

            return ids

    def _validate_keys(self, keys: Iterable[str]) -> None:
        """
        Validate that all keys are known in the schema.

        Args:
            keys: Iterable of key names to validate

        Raises:
            UnknownKeyError: If any key is not in schema
        """
        schema_keys = set(self._data['keys'])
        input_keys = set(keys)

        # Check for unknown keys
        unknown_keys = input_keys - schema_keys
        if unknown_keys and schema_keys:  # Only enforce if schema is not empty
            raise UnknownKeyError(f"Unknown keys: {sorted(unknown_keys)}")

        # Check for missing required keys (when schema is not empty)
        if schema_keys:
            missing_keys = schema_keys - input_keys
            if missing_keys:
                raise UnknownKeyError(f"Missing required keys: {sorted(missing_keys)}")

    def _update_schema(self, keys: Iterable[str]) -> None:
        """
        Update schema with new keys if needed.

        Args:
            keys: Iterable of key names to potentially add to schema
        """
        current_keys = set(self._data['keys'])
        new_keys = set(keys) - current_keys

        if new_keys:
            self._data['keys'] = sorted(current_keys | new_keys)

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all records.

        Returns:
            Dictionary mapping IDs to record data
        """
        with self.lock:
            return self._data['data'].copy()

    def get_by_id(self, record_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific record by its ID.

        Args:
            record_id: ID of the record to retrieve

        Returns:
            Record data

        Raises:
            IdDoesNotExistError: If ID doesn't exist
        """
        with self.lock:
            if record_id not in self._data['data']:
                raise IdDoesNotExistError(f"ID '{record_id}' does not exist")

            return self._data['data'][record_id].copy()

    def get_by_query(self, query_func: QueryFunc) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve records matching a predicate function.

        Args:
            query_func: Function that takes a record dict and returns bool

        Returns:
            Dictionary mapping IDs to matching record data
        """
        if not callable(query_func):
            raise TypeError("query_func must be callable")

        with self.lock:
            result = {}
            for record_id, record in self._data['data'].items():
                try:
                    if query_func(record):
                        result[record_id] = record.copy()
                except (KeyError, TypeError):
                    # Skip records that cause errors in query function
                    continue

            return result

    def get_all_select_keys(self, keys: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Return only specified fields for all records.

        Args:
            keys: List of field names to include

        Returns:
            Dictionary mapping IDs to records with only specified fields

        Raises:
            UnknownKeyError: If any key is not in schema
        """
        with self.lock:
            # Validate all keys exist in schema
            schema_keys = set(self._data['keys'])
            for key in keys:
                if key not in schema_keys:
                    raise UnknownKeyError(f"Key '{key}' is not in schema")

            result = {}
            for record_id, record in self._data['data'].items():
                filtered_record = {}
                for key in keys:
                    if key in record:
                        filtered_record[key] = record[key]
                result[record_id] = filtered_record

            return result

    def update_by_id(self, record_id: str, new_data: Dict[str, Any]) -> None:
        """
        Update specific record fields by ID.

        Args:
            record_id: ID of the record to update
            new_data: Dictionary containing fields to update

        Raises:
            IdDoesNotExistError: If ID doesn't exist
            UnknownKeyError: If new_data contains unknown fields
        """
        if not isinstance(new_data, dict):
            raise TypeError("new_data must be a dictionary")

        with self.lock:
            if record_id not in self._data['data']:
                raise IdDoesNotExistError(f"ID '{record_id}' does not exist")

            # Validate new keys
            current_keys = set(self._data['data'][record_id].keys())
            new_keys = set(new_data.keys())

            # Check for unknown keys (keys not in schema)
            schema_keys = set(self._data['keys'])
            unknown_keys = new_keys - schema_keys
            if unknown_keys:
                raise UnknownKeyError(f"Unknown keys: {sorted(unknown_keys)}")

            # Update record
            updated_record = self._data['data'][record_id].copy()
            updated_record.update(new_data)

            # Sort keys alphabetically
            sorted_record = {k: updated_record[k] for k in sorted(updated_record.keys())}

            self._data['data'][record_id] = sorted_record

            if self.auto_dump:
                self._dump()

    def update_by_query(self, query_func: QueryFunc, new_data: Dict[str, Any]) -> int:
        """
        Batch update records matching a predicate.

        Args:
            query_func: Function that takes a record dict and returns bool
            new_data: Dictionary containing fields to update

        Returns:
            Number of records updated

        Raises:
            UnknownKeyError: If new_data contains unknown fields
        """
        if not isinstance(new_data, dict):
            raise TypeError("new_data must be a dictionary")

        if not callable(query_func):
            raise TypeError("query_func must be callable")

        with self.lock:
            # Validate new keys against schema
            schema_keys = set(self._data['keys'])
            new_keys = set(new_data.keys())
            unknown_keys = new_keys - schema_keys
            if unknown_keys:
                raise UnknownKeyError(f"Unknown keys: {sorted(unknown_keys)}")

            updated_count = 0
            for record_id, record in self._data['data'].items():
                try:
                    if query_func(record):
                        # Update record
                        updated_record = record.copy()
                        updated_record.update(new_data)

                        # Sort keys alphabetically
                        sorted_record = {k: updated_record[k] for k in sorted(updated_record.keys())}

                        self._data['data'][record_id] = sorted_record
                        updated_count += 1
                except (KeyError, TypeError):
                    # Skip records that cause errors in query function
                    continue

            if updated_count > 0 and self.auto_dump:
                self._dump()

            return updated_count

    def delete_by_id(self, record_id: str) -> bool:
        """
        Delete a specific record by ID.

        Args:
            record_id: ID of the record to delete

        Returns:
            True if record was deleted, False if ID didn't exist
        """
        with self.lock:
            if record_id in self._data['data']:
                del self._data['data'][record_id]
                if self.auto_dump:
                    self._dump()
                return True
            return False

    def delete_by_query(self, query_func: QueryFunc) -> int:
        """
        Batch delete records matching a predicate.

        Args:
            query_func: Function that takes a record dict and returns bool

        Returns:
            Number of records deleted
        """
        if not callable(query_func):
            raise TypeError("query_func must be callable")

        with self.lock:
            to_delete = []
            for record_id, record in self._data['data'].items():
                try:
                    if query_func(record):
                        to_delete.append(record_id)
                except (KeyError, TypeError):
                    # Skip records that cause errors in query function
                    continue

            for record_id in to_delete:
                del self._data['data'][record_id]

            if to_delete and self.auto_dump:
                self._dump()

            return len(to_delete)

    def purge(self) -> None:
        """Clear all data while preserving database structure."""
        with self.lock:
            self._data['data'] = {}
            if self.auto_dump:
                self._dump()

    def add_new_key(self, key: str, default_value: Any = None) -> None:
        """
        Add a new field to all existing records with a default value.

        Args:
            key: New field name
            default_value: Default value for existing records
        """
        with self.lock:
            # Add to schema if not already present
            if key not in self._data['keys']:
                self._data['keys'] = sorted(self._data['keys'] + [key])

            # Add to all existing records
            for record_id in self._data['data']:
                if key not in self._data['data'][record_id]:
                    self._data['data'][record_id][key] = default_value

            # Sort keys in each record
            for record_id, record in self._data['data'].items():
                sorted_record = {k: record[k] for k in sorted(record.keys())}
                self._data['data'][record_id] = sorted_record

            if self.auto_dump:
                self._dump()

    def commit(self) -> None:
        """Manually save changes to file (useful when auto_dump=False)."""
        self._dump()