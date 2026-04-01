import json
path = 'tests/enhanced_test_cases/feature2_custom_ids.json'
with open(path, 'r') as f:
    data = json.load(f)
cases = data['cases']
# indices of new cases: original 3 cases, new cases start at index 3
# Remove cases at index 6 and 5? Let's print descriptions
for i, case in enumerate(cases):
    print(i, case.get('input', {}).get('ids', 'no ids'))
# We'll remove the two with Unicode and leading number
# They are at positions 6 and 5? Actually order: after first three new cases (ids with None, param id=None, param without id) -> index 3,4,5
# Then Unicode index 6, leading number index 7, underscore index 8, empty string index 9
# Let's remove indices 6 and 7
del cases[6]
del cases[6]  # after first deletion, indices shift
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
print("Removed two cases.")