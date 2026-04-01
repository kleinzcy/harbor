import json

file_path = '/Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/pysondb-v2/tests/enhanced_test_cases/feature4_cli.json'
with open(file_path, 'r') as f:
    data = json.load(f)

cases = data['cases']

new_cases = [
    # 5. Unknown CLI command
    {
        "input": {"command": "unknown"},
        "expected_output": {"status": "error", "error_type": "ValueError"}
    },
    # 6. CLI show with non-existent db_file (should still succeed because PysonDB creates empty db)
    # We'll test that it returns some output
    {
        "input": {"command": "show", "db_file": "non_existent.json"},
        "expected_output": {"status": "success", "format": "table", "row_count": 0}
    },
    # 7. CLI merge with empty db_files list (should error)
    {
        "input": {"command": "merge", "db_files": [], "output": "merged.json"},
        "expected_output": {"status": "error"}
    },
    # 8. CLI tocsv with non-existent db_file (creates empty db)
    {
        "input": {"command": "tocsv", "db_file": "empty.json", "output": "empty.csv"},
        "expected_output": {"status": "success", "file_exists": True, "lines": 1}  # header only
    }
]

cases.extend(new_cases)
data['cases'] = cases

with open(file_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Enhanced feature4 with {len(new_cases)} new cases")