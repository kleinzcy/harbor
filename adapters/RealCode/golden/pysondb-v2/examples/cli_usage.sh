#!/bin/bash
# CLI usage examples for pysonDB-v2

echo "=== pysonDB-v2 CLI Examples ==="
echo

# Create a test database
echo "1. Creating a test database..."
cat > test_data.json << EOF
{
  "version": 2,
  "keys": ["name", "age", "email"],
  "data": {
    "1": {"name": "Alice", "age": 30, "email": "alice@example.com"},
    "2": {"name": "Bob", "age": 25, "email": "bob@example.com"},
    "3": {"name": "Charlie", "age": 35, "email": "charlie@example.com"}
  }
}
EOF

echo "2. Displaying database info:"
python3 -m pysondb info

echo
echo "3. Showing database as table:"
python3 -m pysondb show test_data.json

echo
echo "4. Exporting to CSV:"
python3 -m pysondb tocsv test_data.json --output test_data.csv
echo "Lines in CSV: $(wc -l < test_data.csv)"

echo
echo "5. Creating second database for merging..."
cat > test_data2.json << EOF
{
  "version": 2,
  "keys": ["name", "age", "email"],
  "data": {
    "4": {"name": "David", "age": 40, "email": "david@example.com"},
    "5": {"name": "Eve", "age": 28, "email": "eve@example.com"}
  }
}
EOF

echo "6. Merging databases:"
python3 -m pysondb merge test_data.json test_data2.json --output merged.json
echo "Merged database created: merged.json"

echo
echo "7. Purging a database:"
python3 -m pysondb purge merged.json
echo "Purged merged.json"

echo
echo "8. Migrating from v1 format (example):"
cat > v1_database.json << EOF
{
  "data": [
    {"id": 1, "name": "Old User", "age": 50},
    {"id": 2, "name": "Another User", "age": 45}
  ]
}
EOF
python3 -m pysondb migrate v1_database.json migrated_v2.json --indent 2
echo "Migrated to migrated_v2.json"

# Clean up
rm -f test_data.json test_data2.json merged.json v1_database.json migrated_v2.json test_data.csv

echo
echo "=== Examples completed ==="