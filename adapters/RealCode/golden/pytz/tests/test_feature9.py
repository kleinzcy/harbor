#!/usr/bin/env python3
"""
Test script for Feature 9: Timezone Serialization
"""

import sys
import os
import json
import pickle

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz


def test_serialization():
    """Test pickle serialization and deserialization of timezone objects."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature9_serialization.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            expected = test_case['expected_output']
            
            # Handle different test types
            if 'type' in input_data and input_data['type'] == 'FixedOffset':
                # FixedOffset serialization test
                offset_minutes = input_data['offset_minutes']
                
                # Create FixedOffset
                tz = pytz.FixedOffset(offset_minutes)
                
                # Serialize and deserialize
                pickled = pickle.dumps(tz)
                unpickled = pickle.loads(pickled)
                
                # Check if same object (singleton preserved)
                same_object = tz is unpickled
                
                if same_object != expected['same_object_after_roundtrip']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"FixedOffset singleton preservation failed: expected same_object={expected['same_object_after_roundtrip']}, got {same_object}"
                    })
                    continue
                
                # Check repr
                repr_str = repr(unpickled)
                if repr_str != expected['repr']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"FixedOffset repr mismatch: expected {expected['repr']}, got {repr_str}"
                    })
                    continue
                
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"FixedOffset serialization passed: offset={offset_minutes}, singleton preserved"
                })
            
            elif 'check' in input_data and input_data['check'] == 'compact_serialization':
                # UTC compact serialization test
                # Compare serialization size of UTC vs DST timezone
                utc_tz = pytz.UTC
                dst_tz = pytz.timezone('US/Eastern')
                
                utc_size = len(pickle.dumps(utc_tz))
                dst_size = len(pickle.dumps(dst_tz))
                
                utc_smaller = utc_size < dst_size
                
                if utc_smaller != expected['utc_smaller_than_dst']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"UTC compact serialization failed: expected utc_smaller_than_dst={expected['utc_smaller_than_dst']}, got {utc_smaller} (UTC size={utc_size}, DST size={dst_size})"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"UTC compact serialization passed: UTC size={utc_size}, DST size={dst_size}"
                    })
            
            else:
                # Regular timezone serialization test
                zone = input_data['zone']
                
                # Create timezone
                tz = pytz.timezone(zone)
                
                # Serialize and deserialize
                pickled = pickle.dumps(tz)
                unpickled = pickle.loads(pickled)
                
                # Check if same object (singleton preserved)
                same_object = tz is unpickled
                
                if same_object != expected['same_object_after_roundtrip']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Timezone singleton preservation failed for {zone}: expected same_object={expected['same_object_after_roundtrip']}, got {same_object}"
                    })
                    continue
                
                # Check zone
                if unpickled.zone != expected['zone']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Timezone zone mismatch: expected {expected['zone']}, got {unpickled.zone}"
                    })
                    continue
                
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"Timezone serialization passed: {zone}, singleton preserved"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_feature9():
    """Run all test cases for Feature 9."""
    print("Feature 9 Test Results:")
    print("======================")
    
    # Run all sub-tests
    all_results = test_serialization()
    
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
    success = test_feature9()
    sys.exit(0 if success else 1)