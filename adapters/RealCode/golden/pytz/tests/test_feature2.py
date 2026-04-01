#!/usr/bin/env python3
"""
Test script for Feature 2: Lazy Collection Classes
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz


def test_feature2():
    """Run all test cases for Feature 2."""
    # Load test cases
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature2_lazy_collections.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            class_name = input_data['class']
            fill_data = input_data['fill_data']
            operation = input_data['operation']
            expected = test_case['expected_output']
            
            # Create fill function
            def make_fill_func(data):
                call_count = [0]
                def fill_func():
                    call_count[0] += 1
                    if class_name == 'LazyList':
                        return list(data)
                    elif class_name == 'LazySet':
                        return set(data) if isinstance(data, list) else data
                    else:  # LazyDict
                        return dict(data)
                fill_func.call_count = call_count
                return fill_func
            
            fill_func = make_fill_func(fill_data)
            
            # Create lazy collection
            if class_name == 'LazyList':
                collection = pytz.LazyList(fill_func)
            elif class_name == 'LazySet':
                collection = pytz.LazySet(fill_func)
            else:  # LazyDict
                collection = pytz.LazyDict(fill_func)
            
            # Check that fill function hasn't been called yet
            if fill_func.call_count[0] != 0:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Fill function called prematurely for {class_name}"
                })
                continue
            
            # Perform operation
            if operation == 'len':
                result = len(collection)
            elif operation == 'getitem':
                if class_name == 'LazyList':
                    result = collection[input_data['index']]
                else:  # LazyDict
                    result = collection[input_data['key']]
            elif operation == 'contains':
                result = input_data['value'] in collection
            elif operation == 'list':
                result = list(collection)
            elif operation == 'keys':
                result = list(collection.keys())
            else:
                results.append({
                    'case': i,
                    'status': 'ERROR',
                    'message': f"Unknown operation: {operation}"
                })
                continue
            
            # Check that fill function was called
            if fill_func.call_count[0] != 1:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Fill function not called or called multiple times for {class_name}"
                })
                continue
            
            # Check result
            if result == expected:
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"{class_name}.{operation}() returned expected value"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"{class_name}.{operation}() returned {result}, expected {expected}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    # Print summary
    print("Feature 2 Test Results:")
    print("======================")
    
    passes = sum(1 for r in results if r['status'] == 'PASS')
    fails = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"Total: {len(results)}, Pass: {passes}, Fail: {fails}, Error: {errors}")
    print()
    
    # Print detailed results
    for result in results:
        status_symbol = '✓' if result['status'] == 'PASS' else '✗' if result['status'] == 'FAIL' else '!'
        print(f"{status_symbol} Case {result['case']}: {result['message']}")
    
    return fails == 0 and errors == 0


if __name__ == '__main__':
    success = test_feature2()
    sys.exit(0 if success else 1)