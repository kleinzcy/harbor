#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_expected import ExpectedOutputGenerator

generator = ExpectedOutputGenerator()

# Test case for groupby_rolling
test_case = {
    "input": {
        "operation": "groupby_rolling",
        "group_col": "a",
        "window": 4,
        "df_size": 150,
        "func": "lambda w: w.sum(numeric_only=True)"
    },
    "expected_output": ""  # Placeholder
}

output = generator.compute_expected_output(test_case)
print("Generated output (first 500 chars):")
print(output[:500])
print("\nFull first few lines:")
lines = output.split('\n')
for i in range(min(10, len(lines))):
    print(f"{i}: {repr(lines[i])}")

# Also test groupby_expanding
test_case2 = {
    "input": {
        "operation": "groupby_expanding",
        "group_col": "a",
        "df_size": 150,
        "func": "lambda w: w.min()"
    },
    "expected_output": ""
}

output2 = generator.compute_expected_output(test_case2)
print("\n\nGroupby expanding output (first 500 chars):")
print(output2[:500])
print("\nFull first few lines:")
lines2 = output2.split('\n')
for i in range(min(10, len(lines2))):
    print(f"{i}: {repr(lines2[i])}")