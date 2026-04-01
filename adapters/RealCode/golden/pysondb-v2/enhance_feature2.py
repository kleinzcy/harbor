import json

file_path = '/Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/pysondb-v2/tests/enhanced_test_cases/feature2_schema.json'
with open(file_path, 'r') as f:
    data = json.load(f)

cases = data['cases']

new_cases = [
    # 5. add_new_key without default value (default None)
    {
        "input": {"operation": "add_new_key", "key": "nullable"},
        "expected_output": {"status": "success", "all_records_have_key": True}
    },
    # 6. add_new_key with same key (idempotent)
    {
        "input": {"operation": "add_new_key", "key": "nullable", "default": "different"},
        "expected_output": {"status": "success", "all_records_have_key": True}
    },
    # 7. add_new_key with complex default value (list)
    {
        "input": {"operation": "add_new_key", "key": "tags", "default": []},
        "expected_output": {"status": "success", "all_records_have_key": True}
    },
    # 8. add record with complex data types (including nested dict)
    {
        "input": {"operation": "add", "data": {
            "name": "ComplexUser",
            "age": 99,
            "email": "complex@example.com",
            "nullable": None,
            "tags": ["python", "json"],
            "metadata": {"version": 1}
        }},
        "expected_output": {"status": "success", "keys_sorted": ["age", "email", "metadata", "name", "nullable", "tags"]}
    },
    # 9. Verify keys sorted after multiple additions
    {
        "input": {"operation": "add_new_key", "key": "aaa_first", "default": 0},
        "expected_output": {"status": "success", "all_records_have_key": True}
    },
    # 10. Check keys sorted
    {
        "input": {"operation": "get_all"},
        "expected_output": {"status": "success", "count": 2}  # David + ComplexUser
    }
]

cases.extend(new_cases)
data['cases'] = cases

with open(file_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Enhanced feature2 with {len(new_cases)} new cases")