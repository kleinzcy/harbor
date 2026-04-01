# pysonDB-v2 - Lightweight JSON Database Library

## Project Goal

Build a lightweight JSON-based database library that allows developers to perform full CRUD operations on local JSON files without requiring a traditional database server. The library provides a simple, intuitive API for data storage, retrieval, updating, and deletion, along with a command-line interface for direct database management, enabling rapid prototyping and small-scale data persistence.

---

## Background & Problem

Without this library/tool, developers are forced to manually read/write JSON files with custom parsing logic, implement their own CRUD operations, handle concurrency issues, validate data schemas, and maintain boilerplate code for every project requiring simple data persistence. This leads to repetitive code, error-prone implementations, inconsistent error handling, and maintenance overhead across projects.

With this library/tool, developers can leverage a consistent, well-tested API for JSON-based data storage that handles schema evolution, automatic ID generation, type validation, and concurrent access, dramatically simplifying data persistence for small projects, prototypes, and automation scripts.

---

## Core Features

### Feature 1: Core CRUD Operations

**As a developer**, I want to perform basic Create, Read, Update, and Delete operations on JSON data, so I can manage persistent data without writing boilerplate file I/O code.

**Expected Behavior / Usage:**

The library should provide methods for:
- `add(data)`: Add a single record with auto-generated ID, returning the ID
- `add_many(data_list)`: Add multiple records in batch, with optional JSON response
- `get_all()`: Retrieve all records as `{id: data}` dictionary
- `get_by_id(id)`: Retrieve a specific record by its ID
- `get_by_query(query_func)`: Retrieve records matching a predicate function
- `update_by_id(id, new_data)`: Update specific record fields by ID
- `update_by_query(query_func, new_data)`: Batch update records matching a predicate
- `delete_by_id(id)`: Delete a specific record by ID
- `delete_by_query(query_func)`: Batch delete records matching a predicate
- `purge()`: Clear all data while preserving database structure

All operations should maintain data consistency, handle concurrent access via locking, and validate inputs against the database schema.

**Test Cases:** `tests/test_cases/feature1_crud.json`

```json
{
    "description": "Basic CRUD operations with single and multiple records",
    "cases": [
        {
            "input": {"operation": "add", "data": {"name": "Alice", "age": 30}},
            "expected_output": {"status": "success", "id_length": 18}
        },
        {
            "input": {"operation": "add_many", "data": [{"name": "Bob", "age": 25}, {"name": "Charlie", "age": 35}]},
            "expected_output": {"status": "success", "count": 2}
        },
        {
            "input": {"operation": "get_all"},
            "expected_output": {"status": "success", "count": 3}
        },
        {
            "input": {"operation": "get_by_id", "id": "123456789012345678"},
            "expected_output": {"status": "success", "data_contains": {"name": "Alice"}}
        },
        {
            "input": {"operation": "update_by_id", "id": "123456789012345678", "new_data": {"age": 31}},
            "expected_output": {"status": "success", "updated_age": 31}
        },
        {
            "input": {"operation": "delete_by_id", "id": "123456789012345678"},
            "expected_output": {"status": "success", "remaining_count": 2}
        }
    ]
}
```

---

### Feature 2: Schema Management and Dynamic Fields

**As a developer**, I want to manage database schema dynamically, adding new fields with default values and validating data types, so I can evolve my data model without breaking existing data.

**Expected Behavior / Usage:**

The library should support:
- `add_new_key(key, default_value)`: Add a new field to all existing records with a default value
- Automatic schema inference from the first added record
- Type validation for supported data types (int, str, bool, list, dict)
- Consistent alphabetical key sorting across all operations
- Custom ID generator via `set_id_generator(func)`

When adding data with new fields not in the schema, the system should raise `UnknownKeyError`. When adding data missing required fields, it should also raise `UnknownKeyError`. The system should maintain a `keys` array in the database schema tracking all known fields.

**Test Cases:** `tests/test_cases/feature2_schema.json`

```json
{
    "description": "Schema evolution and dynamic field management",
    "cases": [
        {
            "input": {"operation": "add_new_key", "key": "email", "default": "unknown@example.com"},
            "expected_output": {"status": "success", "all_records_have_key": true}
        },
        {
            "input": {"operation": "add", "data": {"name": "David", "age": 40, "email": "david@example.com"}},
            "expected_output": {"status": "success", "keys_sorted": ["age", "email", "name"]}
        },
        {
            "input": {"operation": "add", "data": {"name": "Eve", "unknown_field": "value"}},
            "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
        },
        {
            "input": {"operation": "set_id_generator", "generator_type": "sequential"},
            "expected_output": {"status": "success", "next_id_pattern": "1"}
        }
    ]
}
```

---

### Feature 3: Advanced Querying and Filtering

**As a developer**, I want to query data with complex conditions and select specific fields, so I can efficiently retrieve only the data I need without processing entire datasets.

**Expected Behavior / Usage:**

The library should provide:
- `get_by_query(query_func)`: Accept a lambda or function that returns boolean for each record
- `get_all_select_keys(keys)`: Return only specified fields for all records
- Support for complex query conditions (AND, OR, comparisons, string operations)
- Pagination support through query functions with slicing
- Efficient filtering without loading entire dataset into memory unnecessarily

Query functions should receive the complete data dictionary for each record and return True/False. The system should handle missing keys gracefully in queries.

**Test Cases:** `tests/test_cases/feature3_query.json`

```json
{
    "description": "Advanced querying and selective field retrieval",
    "cases": [
        {
            "input": {"operation": "get_by_query", "query": "lambda x: x['age'] > 30"},
            "expected_output": {"status": "success", "match_count": 2}
        },
        {
            "input": {"operation": "get_by_query", "query": "lambda x: x['age'] > 30 and 'example.com' in x['email']"},
            "expected_output": {"status": "success", "match_count": 1}
        },
        {
            "input": {"operation": "get_all_select_keys", "keys": ["name", "email"]},
            "expected_output": {"status": "success", "has_age": false, "has_name": true}
        },
        {
            "input": {"operation": "get_all_select_keys", "keys": ["invalid_key"]},
            "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
        }
    ]
}
```

---

### Feature 4: Command Line Interface

**As a developer**, I want to manage databases directly from the command line, so I can perform operations without writing Python scripts for common tasks.

**Expected Behavior / Usage:**

The CLI should support:
- `python -m pysondb --info`: Display version and JSON parser info
- `python -m pysondb migrate <old> <new> [--indent N]`: Migrate v1 database to v2 format
- `python -m pysondb show <db_file>`: Display database as formatted table
- `python -m pysondb merge <db1> <db2> ... --output <merged>`: Merge multiple databases
- `python -m pysondb tocsv <db_file> [--output <csv_file>]`: Export to CSV format
- `python -m pysondb purge <db_file>`: Clear database contents

Each command should provide clear success/error messages and appropriate exit codes. The `show` command should use `prettytable` for formatted output if available, with fallback to simple formatting.

**Test Cases:** `tests/test_cases/feature4_cli.json`

```json
{
    "description": "Command line interface operations",
    "cases": [
        {
            "input": {"command": "--info"},
            "expected_output": {"status": "success", "contains": ["PysonDB", "JSON parser"]}
        },
        {
            "input": {"command": "show", "db_file": "test_data.json"},
            "expected_output": {"status": "success", "format": "table", "row_count": 3}
        },
        {
            "input": {"command": "merge", "db_files": ["db1.json", "db2.json"], "output": "merged.json"},
            "expected_output": {"status": "success", "message": "DB's merged successfully"}
        },
        {
            "input": {"command": "tocsv", "db_file": "test_data.json", "output": "output.csv"},
            "expected_output": {"status": "success", "file_exists": true, "lines": 4}
        }
    ]
}
```

---

### Feature 5: Database Utilities and Migration

**As a developer**, I want to perform database maintenance operations like migration from old formats, merging databases, and exporting data, so I can manage my data across different formats and systems.

**Expected Behavior / Usage:**

The library should provide utility functions:
- `migrate(old_db_data)`: Convert v1 format (`{"data": [{...}]}`) to v2 format (`{"version": 2, "keys": [], "data": {...}}`)
- `merge_n_db(*dbs)`: Merge multiple v2 databases with same schema
- `print_db_as_table(data)`: Format database as pretty table string
- `purge_db(_)`: Return empty v2 database structure
- CSV export functionality via CLI and potentially programmatic API

Migration should preserve all data while transforming structure. Merging should validate schema compatibility and generate new unique IDs if needed. Export functions should handle large datasets efficiently.

**Test Cases:** `tests/test_cases/feature5_utilities.json`

```json
{
    "description": "Database utilities for migration, merging, and export",
    "cases": [
        {
            "input": {"operation": "migrate", "old_data": {"data": [{"id": 1, "name": "Test", "age": 20}]}},
            "expected_output": {"status": "success", "has_version": 2, "has_keys": true, "data_count": 1}
        },
        {
            "input": {"operation": "merge", "databases": [{"version": 2, "keys": ["name", "age"], "data": {"1": {"name": "A", "age": 25}}}, {"version": 2, "keys": ["name", "age"], "data": {"2": {"name": "B", "age": 30}}}]},
            "expected_output": {"status": "success", "merged_keys": ["age", "name"], "total_records": 2}
        },
        {
            "input": {"operation": "purge_db", "input": "any"},
            "expected_output": {"status": "success", "structure": {"version": 2, "keys": [], "data": {}}}
        }
    ]
}
```

---

### Feature 6: Error Handling and Type Safety

**As a developer**, I want clear, specific exceptions for error conditions, so I can handle failures gracefully and debug issues quickly.

**Expected Behavior / Usage:**

The library should raise appropriate custom exceptions:
- `IdDoesNotExistError`: When operations reference non-existent IDs
- `UnknownKeyError`: When data contains unknown fields or misses required fields
- `SchemaTypeError`: When database structure is invalid or corrupted
- Standard `TypeError`: When parameter types are incorrect

All exceptions should provide informative error messages. The library should validate database file structure on load, ensuring required fields (`version`, `keys`, `data`) exist with correct types. Data type validation should occur on add/update operations.

**Test Cases:** `tests/test_cases/feature6_errors.json`

```json
{
    "description": "Error handling and exception scenarios",
    "cases": [
        {
            "input": {"operation": "get_by_id", "id": "non_existent_123"},
            "expected_output": {"status": "error", "error_type": "IdDoesNotExistError"}
        },
        {
            "input": {"operation": "add", "data": {"unknown_field": "value"}},
            "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
        },
        {
            "input": {"operation": "load_corrupted", "db_file": "corrupted.json"},
            "expected_output": {"status": "error", "error_type": "SchemaTypeError"}
        },
        {
            "input": {"operation": "add", "data": "not_a_dict"},
            "expected_output": {"status": "error", "error_type": "TypeError"}
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_crud.json` should write its output to `tests/stdout/feature1_crud@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.

3. **Complete Python package** with `setup.py` declaring dependencies (ujson==5.2.0, prettytable==3.3.0, pytest==8.4.1, pytest-mock==3.14.1, python>=3.7.0), proper module structure (`pysondb/` with `__init__.py`, `db.py`, `cli.py`, `errors.py`, `utils.py`, etc.), and installation instructions.

4. **Comprehensive documentation** including API reference, usage examples, and CLI command summaries.

5. **Example scripts** demonstrating common workflows: database initialization, CRUD operations, data export, and migration scenarios.