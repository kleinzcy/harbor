import json
path = 'tests/enhanced_test_cases/feature1_basic_parametrization.json'
with open(path, 'r') as f:
    data = json.load(f)
cases = data['cases']
for i, case in enumerate(cases):
    if case.get('input', {}).get('argnames') == '':
        print(f'Found empty argnames case at index {i}')
        # Replace with new case
        cases[i] = {
            "input": {
                "argnames": "x, ,y",
                "argvalues": [[1, 2], [3, 4]]
            },
            "expected_output": {
                "error": "Argument name at index 1 is empty after stripping"
            }
        }
        break
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
print('Replaced empty argnames case.')