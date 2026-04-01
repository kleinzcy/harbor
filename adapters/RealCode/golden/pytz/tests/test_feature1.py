#!/usr/bin/env python3
"""
Test script for Feature 1: Timezone Object Creation and Caching
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz


def test_feature1():
    """Run all test cases for Feature 1."""
    # Load test cases
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature1_timezone_creation.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            action = input_data['action']
            
            if action == 'create':
                zone = input_data['zone']
                try:
                    tz = pytz.timezone(zone)
                    expected = test_case['expected_output']
                    
                    if 'error' in expected:
                        # Should have raised an error
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Expected {expected['error']} but got timezone object"
                        })
                    else:
                        # Check zone attribute
                        if tz.zone != expected['zone']:
                            results.append({
                                'case': i,
                                'status': 'FAIL',
                                'message': f"Expected zone {expected['zone']}, got {tz.zone}"
                            })
                        else:
                            results.append({
                                'case': i,
                                'status': 'PASS',
                                'message': f"Created timezone {tz.zone}"
                            })
                            
                except pytz.UnknownTimeZoneError:
                    expected = test_case['expected_output']
                    if 'error' in expected and expected['error'] == 'UnknownTimeZoneError':
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Correctly raised UnknownTimeZoneError for {zone}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Unexpected UnknownTimeZoneError for {zone}"
                        })
                except Exception as e:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Unexpected error: {type(e).__name__}: {str(e)}"
                    })
            
            elif action == 'singleton_check':
                zone = input_data['zone']
                tz1 = pytz.timezone(zone)
                tz2 = pytz.timezone(zone)
                expected = test_case['expected_output']
                
                if expected['same_object']:
                    if tz1 is tz2:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Singleton check passed for {zone}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Singleton check failed for {zone}"
                        })
                else:
                    if tz1 is not tz2:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Non-singleton check passed for {zone}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Non-singleton check failed for {zone}"
                        })
            
            elif action == 'case_insensitive':
                zone = input_data['zone']
                canonical = input_data['canonical']
                tz = pytz.timezone(zone)
                expected = test_case['expected_output']
                
                if tz.zone == expected['zone']:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Case-insensitive lookup passed: {zone} -> {tz.zone}"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Case-insensitive lookup failed: expected {expected['zone']}, got {tz.zone}"
                    })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    # Print summary
    print("Feature 1 Test Results:")
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
    success = test_feature1()
    sys.exit(0 if success else 1)