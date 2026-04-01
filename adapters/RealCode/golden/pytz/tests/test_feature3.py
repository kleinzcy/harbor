#!/usr/bin/env python3
"""
Test script for Feature 3: Time Localization
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
    
    # Format datetime
    return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} {tzname} ({offset_str})"


def parse_datetime(dt_str):
    """Parse datetime string in YYYY-MM-DD HH:MM:SS format."""
    return datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')


def test_basic_localization():
    """Test basic localization."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature3_1_basic_localization.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            expected = test_case['expected_output']
            
            # Parse datetime
            dt = parse_datetime(dt_str)
            
            # Get timezone
            tz = pytz.timezone(zone)
            
            # Localize
            localized = tz.localize(dt)
            
            # Format result
            result = format_datetime(localized)
            
            # Check result
            if result == expected:
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"Basic localization passed: {dt_str} in {zone}"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Basic localization failed: expected {expected}, got {result}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_ambiguous_time():
    """Test ambiguous time handling."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature3_2_ambiguous_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            expected = test_case['expected_output']
            
            # Parse datetime
            dt = parse_datetime(dt_str)
            
            # Get timezone
            tz = pytz.timezone(zone)
            
            if 'error' in expected:
                # Should raise an error
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Expected {expected['error']} but got localized datetime"
                    })
                except pytz.AmbiguousTimeError:
                    if expected['error'] == 'AmbiguousTimeError':
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Correctly raised AmbiguousTimeError for {dt_str} in {zone}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Unexpected AmbiguousTimeError for {dt_str} in {zone}"
                        })
                except Exception as e:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Unexpected error: {type(e).__name__}: {str(e)}"
                    })
            else:
                # Should localize successfully
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    result = format_datetime(localized)
                    
                    if result == expected:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Ambiguous time handling passed: {dt_str} in {zone} with is_dst={is_dst}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Ambiguous time handling failed: expected {expected}, got {result}"
                        })
                except Exception as e:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Localization error: {type(e).__name__}: {str(e)}"
                    })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_nonexistent_time():
    """Test non-existent time handling."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature3_3_nonexistent_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            expected = test_case['expected_output']
            
            # Parse datetime
            dt = parse_datetime(dt_str)
            
            # Get timezone
            tz = pytz.timezone(zone)
            
            if 'error' in expected:
                # Should raise an error
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Expected {expected['error']} but got localized datetime"
                    })
                except pytz.NonExistentTimeError:
                    if expected['error'] == 'NonExistentTimeError':
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Correctly raised NonExistentTimeError for {dt_str} in {zone}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Unexpected NonExistentTimeError for {dt_str} in {zone}"
                        })
                except Exception as e:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Unexpected error: {type(e).__name__}: {str(e)}"
                    })
            else:
                # Should localize successfully
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    result = format_datetime(localized)
                    
                    if result == expected:
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Non-existent time handling passed: {dt_str} in {zone} with is_dst={is_dst}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Non-existent time handling failed: expected {expected}, got {result}"
                        })
                except Exception as e:
                    results.append({
                        'case': i,
                        'status': 'ERROR',
                        'message': f"Localization error: {type(e).__name__}: {str(e)}"
                    })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_feature3():
    """Run all test cases for Feature 3."""
    print("Feature 3 Test Results:")
    print("======================")
    
    # Run all sub-tests
    all_results = []
    all_results.extend(test_basic_localization())
    all_results.extend(test_ambiguous_time())
    all_results.extend(test_nonexistent_time())
    
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
    success = test_feature3()
    sys.exit(0 if success else 1)