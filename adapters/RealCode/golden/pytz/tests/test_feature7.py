#!/usr/bin/env python3
"""
Test script for Feature 7: Country Timezone Query
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz


def test_country_timezones():
    """Test country timezone lookup functionality."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature7_country_timezones.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            expected = test_case['expected_output']
            country_code = input_data['country_code']
            
            # Get timezones for country
            timezones = pytz.country_timezones(country_code)
            
            # Check expected output
            if 'error' in expected:
                # Should have raised an error
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Expected error {expected['error']} but got timezones: {timezones}"
                })
                continue
            
            # Check exact match if specified
            if 'exact' in expected:
                if timezones == expected['exact']:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Exact match passed for country {country_code}: {timezones}"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Exact match failed for country {country_code}: expected {expected['exact']}, got {timezones}"
                    })
                continue
            
            # Check contains if specified
            all_contained = True
            if 'contains' in expected:
                for tz in expected['contains']:
                    if tz not in timezones:
                        all_contained = False
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Contains check failed for country {country_code}: expected to contain {tz}, got {timezones}"
                        })
                        break
            
            if not all_contained:
                continue
            
            # Check min length if specified
            if 'min_length' in expected:
                if len(timezones) >= expected['min_length']:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Min length check passed for country {country_code}: length {len(timezones)} >= {expected['min_length']}"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Min length check failed for country {country_code}: length {len(timezones)} < {expected['min_length']}"
                    })
                continue
            
            # If we get here, all checks passed
            results.append({
                'case': i,
                'status': 'PASS',
                'message': f"Country timezone test passed for country {country_code}: {timezones}"
            })
        
        except KeyError as e:
            # Check if error was expected
            if 'error' in expected and expected['error'] == 'KeyError':
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"Expected KeyError raised for unknown country code {country_code}: {str(e)}"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Unexpected KeyError for country {country_code}: {str(e)}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_feature7():
    """Run all test cases for Feature 7."""
    print("Feature 7 Test Results:")
    print("======================")
    
    # Run all sub-tests
    all_results = test_country_timezones()
    
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
    success = test_feature7()
    sys.exit(0 if success else 1)