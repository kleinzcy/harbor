#!/usr/bin/env python3
"""
Test script for Feature 6: Fixed Offset Timezone
"""

import sys
import os
import json
import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz


def format_datetime(dt):
    """Format datetime to match test case expected output format."""
    if dt is None:
        return None
    
    # Get timezone abbreviation and offset
    tzname = dt.tzname() or ''
    offset = dt.utcoffset()
    
    if offset is None:
        return str(dt)
    
    # Format offset as ±HHMM
    total_seconds = int(offset.total_seconds())
    hours = total_seconds // 3600
    minutes = (abs(total_seconds) % 3600) // 60
    
    # Format as ±HHMM (no colon)
    if total_seconds >= 0:
        offset_str = f"+{hours:02d}{minutes:02d}"
    else:
        offset_str = f"-{abs(hours):02d}{minutes:02d}"
    
    # For FixedOffset timezones, don't include tzname in output
    # Test expects format: "2002-10-27 06:00:00 (+0800)"
    # Check if it's a FixedOffset by checking the class name
    if dt.tzinfo is not None and 'FixedOffset' in dt.tzinfo.__class__.__name__:
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} ({offset_str})"
    else:
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} {tzname} ({offset_str})"


def parse_datetime(dt_str):
    """Parse datetime string in YYYY-MM-DD HH:MM:SS format."""
    return datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')


def test_fixed_offset():
    """Test FixedOffset timezone creation and functionality."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature6_fixed_offset.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            expected = test_case['expected_output']
            
            # Handle different test types
            if 'action' in input_data and input_data['action'] == 'singleton_check':
                # Singleton check test
                offset_minutes = input_data['offset_minutes']
                
                # Create two FixedOffset objects with same offset
                tz1 = pytz.FixedOffset(offset_minutes)
                tz2 = pytz.FixedOffset(offset_minutes)
                
                # Check if they are the same object
                same_object = tz1 is tz2
                
                if same_object == expected['same_object']:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Singleton check passed: FixedOffset({offset_minutes})"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Singleton check failed: expected same_object={expected['same_object']}, got {same_object}"
                    })
            
            else:
                # Regular fixed offset test
                offset_minutes = input_data['offset_minutes']
                dt_str = input_data['datetime']
                
                # Parse datetime
                dt = parse_datetime(dt_str)
                
                # Create FixedOffset timezone
                tz = pytz.FixedOffset(offset_minutes)
                
                # Make datetime aware
                aware_dt = dt.replace(tzinfo=tz)
                
                # Check formatted output
                formatted = format_datetime(aware_dt)
                if formatted != expected['formatted']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Format failed: expected {expected['formatted']}, got {formatted}"
                    })
                    continue
                
                # Check utcoffset
                utcoffset_str = str(aware_dt.utcoffset())
                if utcoffset_str != expected['utcoffset']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"utcoffset failed: expected {expected['utcoffset']}, got {utcoffset_str}"
                    })
                    continue
                
                # Check dst
                dst_str = str(aware_dt.dst())
                if dst_str != expected['dst']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"dst failed: expected {expected['dst']}, got {dst_str}"
                    })
                    continue
                
                # Check repr
                repr_str = repr(tz)
                if repr_str != expected['repr']:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"repr failed: expected {expected['repr']}, got {repr_str}"
                    })
                    continue
                
                # All checks passed
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"FixedOffset test passed: offset={offset_minutes}, datetime={dt_str}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_feature6():
    """Run all test cases for Feature 6."""
    print("Feature 6 Test Results:")
    print("======================")
    
    # Run all sub-tests
    all_results = test_fixed_offset()
    
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
    success = test_feature6()
    sys.exit(0 if success else 1)