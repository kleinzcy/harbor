import json

file_path = '/Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/pysondb-v2/tests/enhanced_test_cases/feature3_query.json'
with open(file_path, 'r') as f:
    data = json.load(f)

cases = data['cases']

# Prepend setup cases
setup_cases = [
    # Add records with age, email, name
    {
        "input": {"operation": "add", "data": {"name": "Alice", "age": 30, "email": "alice@example.com"}},
        "expected_output": {"status": "success", "id_length": 18}
    },
    {
        "input": {"operation": "add", "data": {"name": "Bob", "age": 25, "email": "bob@example.com"}},
        "expected_output": {"status": "success", "id_length": 18}
    },
    {
        "input": {"operation": "add", "data": {"name": "Charlie", "age": 35, "email": "charlie@example.com"}},
        "expected_output": {"status": "success", "id_length": 18}
    },
    {
        "input": {"operation": "add", "data": {"name": "David", "age": 40, "email": "david@other.com"}},
        "expected_output": {"status": "success", "id_length": 18}
    }
]

# Update existing expected match counts? They expect 2 and 1 matches. With our data:
# ages: 30,25,35,40. age > 30 matches Charlie(35), David(40) -> 2 matches (good)
# age > 30 and email contains 'example.com' matches Charlie only (email charlie@example.com) -> 1 match (good)
# So existing expected outputs remain valid.

new_cases = [
    # Additional test cases after existing ones
    # 5. get_by_query with lambda that raises KeyError (should skip)
    {
        "input": {"operation": "get_by_query", "query": "lambda x: x['nonexistent'] > 0"},
        "expected_output": {"status": "success", "match_count": 0}
    },
    # 6. get_by_query with lambda that returns False for all
    {
        "input": {"operation": "get_by_query", "query": "lambda x: False"},
        "expected_output": {"status": "success", "match_count": 0}
    },
    # 7. get_by_query with OR condition
    {
        "input": {"operation": "get_by_query", "query": "lambda x: x['age'] == 25 or x['age'] == 40"},
        "expected_output": {"status": "success", "match_count": 2}
    },
    # 8. get_all_select_keys with empty list
    {
        "input": {"operation": "get_all_select_keys", "keys": []},
        "expected_output": {"status": "success", "has_age": False, "has_name": False}
    },
    # 9. get_all_select_keys with duplicate keys
    {
        "input": {"operation": "get_all_select_keys", "keys": ["name", "age", "name"]},
        "expected_output": {"status": "success", "has_age": True, "has_name": True}
    },
    # 10. get_all_select_keys with missing key (not in schema) - error already covered
]

# Insert setup at beginning
cases = setup_cases + cases + new_cases
data['cases'] = cases

with open(file_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Enhanced feature3 with {len(setup_cases)} setup cases and {len(new_cases)} new cases")