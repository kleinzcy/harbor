import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'tests')

from tests.test_runner import TestRunner

runner = TestRunner()

# Simulate groupby_rolling test case
test_case = {
    'input': {
        'operation': 'groupby_rolling',
        'group_col': 'a',
        'window': 4,
        'df_size': 150,
        'func': 'lambda w: w.sum(numeric_only=True)'
    },
    'expected_output': 'success'
}

print("Running test case...")
output = runner._run_test_case(test_case)
print("Output:", output)