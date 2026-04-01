import json

file_path = '/Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/pysondb-v2/tests/enhanced_test_cases/feature5_utilities.json'
with open(file_path, 'r') as f:
    data = json.load(f)

cases = data['cases']

new_cases = [
    # 4. merge with mismatched schemas (should raise ValueError)
    {
        "input": {"operation": "merge", "databases": [
            {"version": 2, "keys": ["name", "age"], "data": {"1": {"name": "A", "age": 25}}},
            {"version": 2, "keys": ["age", "email"], "data": {"2": {"age": 30, "email": "test@example.com"}}}
        ]},
        "expected_output": {"status": "error", "error_type": "ValueError"}
    },
    # 5. merge with duplicate IDs (should generate new IDs)
    {
        "input": {"operation": "merge", "databases": [
            {"version": 2, "keys": ["name", "age"], "data": {"1": {"name": "A", "age": 25}}},
            {"version": 2, "keys": ["name", "age"], "data": {"1": {"name": "B", "age": 30}}}
        ]},
        "expected_output": {"status": "success", "total_records": 2}
    },
    # 6. migrate with invalid v1 format (missing 'data')
    {
        "input": {"operation": "migrate", "old_data": {}},
        "expected_output": {"status": "error", "error_type": "SchemaTypeError"}
    },
    # 7. migrate with v1 data containing non-dict records
    {
        "input": {"operation": "migrate", "old_data": {"data": [{"id": 1}, "invalid"]}},
        "expected_output": {"status": "success", "has_version": True, "has_keys": True, "data_count": 1}
    },
    # 8. merge with empty list (should return empty db)
    {
        "input": {"operation": "merge", "databases": []},
        "expected_output": {"status": "success", "merged_keys": [], "total_records": 0}
    },
    # 9. purge_db with null input
    {
        "input": {"operation": "purge_db", "input": None},
        "expected_output": {"status": "success", "structure": {"version": 2, "keys": [], "data": {}}}
    }
]

cases.extend(new_cases)
data['cases'] = cases

with open(file_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Enhanced feature5 with {len(new_cases)} new cases")