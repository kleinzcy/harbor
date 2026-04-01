import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pytz

# Test one specific case
test_case = {
    "input": {
        "class": "LazyList",
        "fill_data": [1, 2, 3],
        "operation": "len"
    },
    "expected_output": 3
}

input_data = test_case['input']
class_name = input_data['class']
fill_data = input_data['fill_data']
operation = input_data['operation']

print(f"Testing {class_name} with {operation}")
print(f"Fill data: {fill_data}")

if class_name == 'LazyList':
    lazy_obj = pytz.LazyList(lambda: fill_data)
    if operation == 'len':
        result = len(lazy_obj)
        print(f"Result: {result}")
        print(f"Expected: {test_case['expected_output']}")
        print(f"Match: {result == test_case['expected_output']}")