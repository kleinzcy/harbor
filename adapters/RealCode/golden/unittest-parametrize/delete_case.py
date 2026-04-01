import json
path = 'tests/enhanced_test_cases/feature1_basic_parametrization.json'
with open(path, 'r') as f:
    data = json.load(f)
cases = data['cases']
# Find case with argnames "x, ,y"
to_delete = None
for i, case in enumerate(cases):
    if case.get('input', {}).get('argnames') == 'x, ,y':
        to_delete = i
        break
if to_delete is not None:
    del cases[to_delete]
    print(f'Deleted case at index {to_delete}')
else:
    print('Case not found')
with open(path, 'w') as f:
    json.dump(data, f, indent=2)