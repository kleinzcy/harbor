import json

file_path = '/Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/pysondb-v2/tests/enhanced_test_cases/feature6_errors.json'
with open(file_path, 'r') as f:
    data = json.load(f)

cases = data['cases']

# Insert setup cases before existing ones
setup_cases = [
    # 0. add_new_key to create schema with keys ["age", "name"]
    {
        "input": {"operation": "add_new_key", "key": "age", "default": 0},
        "expected_output": {"status": "success", "all_records_have_key": True}
    },
    {
        "input": {"operation": "add_new_key", "key": "name", "default": ""},
        "expected_output": {"status": "success", "all_records_have_key": True}
    }
]

new_cases = [
    # 5. add with missing required keys (schema has age, name)
    {
        "input": {"operation": "add", "data": {"age": 30}},
        "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
    },
    # 6. update_by_id unknown field (need an existing record first)
    {
        "input": {"operation": "add", "data": {"age": 25, "name": "Test"}},
        "expected_output": {"status": "success", "id_length": 18}
    },
    {
        "input": {"operation": "update_by_id", "id": "placeholder", "new_data": {"unknown": "value"}},
        "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
    },
    # 8. update_by_id non-existent ID
    {
        "input": {"operation": "update_by_id", "id": "non_existent_999", "new_data": {"age": 99}},
        "expected_output": {"status": "error", "error_type": "IdDoesNotExistError"}
    },
    # 9. add_many with non-list input
    {
        "input": {"operation": "add_many", "data": {}},
        "expected_output": {"status": "error", "error_type": "TypeError"}
    },
    # 10. add_many with list containing non-dict
    {
        "input": {"operation": "add_many", "data": [{"age": 1, "name": "ok"}, "not dict"]},
        "expected_output": {"status": "error", "error_type": "TypeError"}
    },
    # 11. get_by_query with non-callable (pass integer)
    {
        "input": {"operation": "get_by_query", "query": 123},
        "expected_output": {"status": "error", "error_type": "TypeError"}
    },
    # 12. SchemaTypeError for missing version (already covered by load_corrupted)
]

# Combine: setup + original cases + new cases
original_cases = cases
cases = setup_cases + original_cases + new_cases
data['cases'] = cases

with open(file_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Enhanced feature6 with {len(setup_cases)} setup cases and {len(new_cases)} new cases")