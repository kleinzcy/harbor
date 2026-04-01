#!/usr/bin/env python3
"""
Test script for Feature 10: Timezone Collections and Metadata
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz


def test_collections_metadata():
    """Test timezone collections and metadata."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature10_collections_metadata.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            expected = test_case['expected_output']
            
            # Handle different test types
            if 'collection' in input_data:
                collection_name = input_data['collection']
                check = input_data['check']
                
                # Get collection
                if collection_name == 'all_timezones':
                    collection = pytz.all_timezones
                elif collection_name == 'common_timezones':
                    collection = pytz.common_timezones
                else:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Unknown collection: {collection_name}"
                    })
                    continue
                
                # Perform check
                if check == 'contains':
                    value = input_data['value']
                    contains = value in collection
                    
                    if contains == expected:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Collection {collection_name} contains check passed: {value} in collection = {contains}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Collection {collection_name} contains check failed: expected {value} in collection = {expected}, got {contains}"
                        })
                
                elif check == 'min_length':
                    min_length = expected
                    actual_length = len(collection)
                    
                    if actual_length >= min_length:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Collection {collection_name} min length check passed: length {actual_length} >= {min_length}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Collection {collection_name} min length check failed: length {actual_length} < {min_length}"
                        })
                
                elif check == 'is_list':
                    is_list = isinstance(collection, list) or hasattr(collection, '__getitem__')
                    
                    if is_list == expected:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Collection {collection_name} is_list check passed: is_list = {is_list}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Collection {collection_name} is_list check failed: expected is_list = {expected}, got {is_list}"
                        })
                
                else:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Unknown check: {check}"
                    })
            
            elif 'attribute' in input_data:
                attribute_name = input_data['attribute']
                check = input_data['check']
                
                # Get attribute
                if hasattr(pytz, attribute_name):
                    attribute = getattr(pytz, attribute_name)
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Attribute {attribute_name} not found in pytz module"
                    })
                    continue
                
                # Perform check
                if check == 'is_string':
                    is_string = isinstance(attribute, str)
                    
                    if is_string == expected:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Attribute {attribute_name} is_string check passed: is_string = {is_string}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Attribute {attribute_name} is_string check failed: expected is_string = {expected}, got {is_string} (type: {type(attribute).__name__})"
                        })
                
                else:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Unknown check: {check}"
                    })
            
            else:
                results.append({
                    'case': i,
                    'status': 'ERROR',
                    'message': f"Unknown test type: {input_data}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_feature10():
    """Run all test cases for Feature 10."""
    print("Feature 10 Test Results:")
    print("======================")
    
    # Run all sub-tests
    all_results = test_collections_metadata()
    
    # Print summary
    passes = sum(1 for r in all_results if r['status'] == 'PASS')
    fails = sum(1 for r in all_results if r['status'] == 'FAIL')
    errors = sum(1 for r in all_results if r['status'] == 'ERROR')
    
    print(f"Total: {len(all_results)}, Pass: {passes}, Fail: {fails}, Error: {errors}")
    print()
    
    # Print detailed results
    for result in all_results:
        status_symbol = '✓' if result['status'] == 'PASS' else '✗' if result['status'] == 'FAIL' else '!'
        print(f"{status_symbol} Case {result['case']}: {result['message']}")
    
    return fails == 0 and errors == 0


if __name__ == '__main__':
    success = test_feature10()
    sys.exit(0 if success else 1)