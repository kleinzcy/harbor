import json

original = {
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

new_cases = [
    # 7. add empty dict -> missing required keys
    {
        "input": {"operation": "add", "data": {}},
        "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
    },
    # 8. add only age -> missing name
    {
        "input": {"operation": "add", "data": {"age": 40}},
        "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
    },
    # 9. add only name -> missing age
    {
        "input": {"operation": "add", "data": {"name": "David"}},
        "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
    },
    # 10. add with extra unknown key -> unknown key
    {
        "input": {"operation": "add", "data": {"name": "Eve", "age": 50, "extra": "value"}},
        "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
    },
    # 11. add valid record
    {
        "input": {"operation": "add", "data": {"name": "Frank", "age": 60}},
        "expected_output": {"status": "success", "id_length": 18}
    },
    # 12. get_all count should be 3 (Bob, Charlie, Frank)
    {
        "input": {"operation": "get_all"},
        "expected_output": {"status": "success", "count": 3}
    },
    # 13. update_by_id with unknown field (using ID from previous add)
    {
        "input": {"operation": "update_by_id", "id": "placeholder", "new_data": {"unknown_field": "value"}},
        "expected_output": {"status": "error", "error_type": "UnknownKeyError"}
    },
    # 14. update_by_id with valid field (age)
    {
        "input": {"operation": "update_by_id", "id": "placeholder", "new_data": {"age": 65}},
        "expected_output": {"status": "success", "updated_age": 65}
    },
    # 15. delete_by_id with that ID
    {
        "input": {"operation": "delete_by_id", "id": "placeholder"},
        "expected_output": {"status": "success", "remaining_count": 2}
    }
]

original['cases'].extend(new_cases)

with open('/Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/pysondb-v2/tests/enhanced_test_cases/feature1_crud.json', 'w') as f:
    json.dump(original, f, indent=4)

print("Enhanced feature1 written")