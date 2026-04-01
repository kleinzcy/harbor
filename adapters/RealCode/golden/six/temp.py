#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from six import classify_type

new_inputs = [
    "",  # empty string
    "00123",
    "12345678901234567890",
    "café",
    "   ",
    "-0",
    "1.23e-5",
    "1.0",
    "1.",
    "0x10",
    "0b101",
    "123abc",
]

for inp in new_inputs:
    # Simulate the feature2.py parsing
    value = None
    try:
        value = int(inp)
    except ValueError:
        try:
            value = float(inp)
        except ValueError:
            value = inp
    result = classify_type(value)
    print(f'{{"input": "{inp}", "expected_output": "{result}"}}')