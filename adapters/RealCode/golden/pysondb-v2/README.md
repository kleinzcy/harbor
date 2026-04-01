# pysonDB-v2

A lightweight JSON-based database library for Python that provides full CRUD operations on local JSON files without requiring a traditional database server.

## Features

- **Full CRUD operations**: Create, read, update, and delete records with auto-generated IDs
- **Schema management**: Dynamic field addition with default values and type validation
- **Advanced querying**: Filter records with lambda functions and select specific fields
- **Command-line interface**: Manage databases directly from the terminal
- **Database utilities**: Migrate from v1 format, merge databases, export to CSV
- **Error handling**: Clear, specific exceptions for all error conditions
- **Thread-safe**: Locking mechanism for concurrent access
- **Auto-commit**: Optional automatic saving to file

## Installation

```bash
pip install pysondb-v2
```

Or from source:

```bash
git clone https://github.com/example/pysondb-v2.git
cd pysondb-v2
pip install -e .
```

## Quick Start

```python
from pysondb import PysonDB

# Create or load a database
db = PysonDB('mydb.json')

# Add a record
record_id = db.add({'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
print(f"Added record with ID: {record_id}")

# Retrieve all records
all_records = db.get_all()
print(f"Total records: {len(all_records)}")

# Query records
adults = db.get_by_query(lambda x: x['age'] >= 18)
print(f"Adults: {len(adults)}")

# Update a record
db.update_by_id(record_id, {'age': 31})

# Delete a record
db.delete_by_id(record_id)
```

## Command Line Interface

```bash
# Display version info
python -m pysondb info

# Migrate v1 database to v2 format
python -m pysondb migrate old_db.json new_db.json --indent 2

# Display database as formatted table
python -m pysondb show mydb.json

# Merge multiple databases
python -m pysondb merge db1.json db2.json --output merged.json

# Export to CSV
python -m pysondb tocsv mydb.json --output data.csv

# Clear database contents
python -m pysondb purge mydb.json
```

## Database Schema

pysonDB-v2 uses the following JSON structure:

```json
{
  "version": 2,
  "keys": ["age", "email", "name"],
  "data": {
    "abc123def456ghi789": {
      "age": 30,
      "email": "alice@example.com",
      "name": "Alice"
    }
  }
}
```

- `version`: Always 2 for v2 databases
- `keys`: Alphabetically sorted list of all known field names
- `data`: Dictionary mapping record IDs to record data

## API Reference

### PysonDB Class

#### `__init__(filepath, auto_dump=True, indent=2)`
Initialize database connection.

- `filepath`: Path to JSON database file
- `auto_dump`: Whether to automatically save changes to file (default: True)
- `indent`: JSON indentation level for pretty printing (default: 2)

#### Core Methods

- `add(record)`: Add single record, returns generated ID
- `add_many(records)`: Add multiple records, returns list of IDs
- `get_all()`: Retrieve all records
- `get_by_id(record_id)`: Retrieve specific record by ID
- `get_by_query(query_func)`: Retrieve records matching predicate function
- `get_all_select_keys(keys)`: Retrieve only specified fields for all records
- `update_by_id(record_id, new_data)`: Update specific record
- `update_by_query(query_func, new_data)`: Batch update matching records
- `delete_by_id(record_id)`: Delete specific record
- `delete_by_query(query_func)`: Batch delete matching records
- `purge()`: Clear all data while preserving structure
- `add_new_key(key, default_value)`: Add new field to all records
- `set_id_generator(generator)`: Set custom ID generator function
- `commit()`: Manually save changes (when auto_dump=False)

### Custom Exceptions

- `IdDoesNotExistError`: Raised when referencing non-existent IDs
- `UnknownKeyError`: Raised for unknown fields or missing required fields
- `SchemaTypeError`: Raised for invalid or corrupted database structure

## Examples

### Schema Evolution

```python
# Add a new field to all existing records
db.add_new_key('subscription', 'free')

# Now all records have 'subscription' field with value 'free'
```

### Advanced Querying

```python
# Complex query with multiple conditions
results = db.get_by_query(
    lambda x: x['age'] > 25 and
              x['subscription'] == 'premium' and
              'gmail.com' in x['email']
)

# Select specific fields
names_only = db.get_all_select_keys(['name', 'email'])
```

### Custom ID Generation

```python
import uuid

# Use UUID v4
db.set_id_generator(lambda: str(uuid.uuid4()))

# Or sequential IDs
counter = 0
def sequential_id():
    global counter
    counter += 1
    return str(counter)

db.set_id_generator(sequential_id)
```

## Testing

Run the test suite:

```bash
bash tests/test.sh
```

The test suite executes all test cases defined in `tests/test_cases/` and saves outputs to `tests/stdout/`.

## License

MIT