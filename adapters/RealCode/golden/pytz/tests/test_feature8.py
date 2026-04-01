#!/usr/bin/env python3
"""
Test script for Feature 8: Error Handling and Exceptions
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


def test_unknown_timezone():
    """Test UnknownTimeZoneError for invalid timezone names."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature8_1_unknown_timezone.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            expected = test_case['expected_output']
            zone = input_data['zone']
            
            # Try to create timezone
            tz = pytz.timezone(zone)
            
            # If we get here and error was expected, it's a failure
            if expected['error'] is not None:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Expected {expected['error']} for zone '{zone}' but got timezone: {tz}"
                })
            else:
                # Check zone name
                if tz.zone == expected['zone']:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Valid timezone created: {zone}"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Timezone zone mismatch: expected {expected['zone']}, got {tz.zone}"
                    })
        
        except pytz.UnknownTimeZoneError as e:
            # Check if error was expected
            if expected['error'] == 'UnknownTimeZoneError':
                # Check if it should be a KeyError
                if expected.get('is_key_error', False):
                    if isinstance(e, KeyError):
                        results.append({
                            'case': i,
                            'status': 'PASS',
                            'message': f"Expected UnknownTimeZoneError (KeyError) raised for zone '{zone}': {str(e)}"
                        })
                    else:
                        results.append({
                            'case': i,
                            'status': 'FAIL',
                            'message': f"Expected KeyError subclass but got: {type(e).__name__}"
                        })
                else:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Expected UnknownTimeZoneError raised for zone '{zone}': {str(e)}"
                    })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Unexpected UnknownTimeZoneError for zone '{zone}': {str(e)}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_ambiguous_time():
    """Test AmbiguousTimeError for ambiguous times during DST fall-back."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature8_2_ambiguous_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            expected = test_case['expected_output']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            
            # Parse datetime
            dt = parse_datetime(dt_str)
            
            # Get timezone
            tz = pytz.timezone(zone)
            
            # Try to localize
            localized = tz.localize(dt, is_dst=is_dst)
            
            # If we get here and error was expected, it's a failure
            if expected['error'] is not None:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Expected {expected['error']} for {dt_str} in {zone} but got localized datetime"
                })
            else:
                # Check formatted output
                formatted = format_datetime(localized)
                if formatted == expected['formatted']:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Non-ambiguous time localized successfully: {formatted}"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Format mismatch: expected {expected['formatted']}, got {formatted}"
                    })
        
        except pytz.AmbiguousTimeError as e:
            # Check if error was expected
            if expected['error'] == 'AmbiguousTimeError':
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"Expected AmbiguousTimeError raised for {dt_str} in {zone}: {str(e)}"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Unexpected AmbiguousTimeError for {dt_str} in {zone}: {str(e)}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_nonexistent_time():
    """Test NonExistentTimeError for non-existent times during DST spring-forward."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature8_3_nonexistent_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            expected = test_case['expected_output']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            
            # Parse datetime
            dt = parse_datetime(dt_str)
            
            # Get timezone
            tz = pytz.timezone(zone)
            
            # Try to localize
            localized = tz.localize(dt, is_dst=is_dst)
            
            # If we get here and error was expected, it's a failure
            if expected['error'] is not None:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Expected {expected['error']} for {dt_str} in {zone} but got localized datetime"
                })
            else:
                # Check formatted output
                formatted = format_datetime(localized)
                if formatted == expected['formatted']:
                    results.append({
                        'case': i,
                        'status': 'PASS',
                        'message': f"Existent time localized successfully: {formatted}"
                    })
                else:
                    results.append({
                        'case': i,
                        'status': 'FAIL',
                        'message': f"Format mismatch: expected {expected['formatted']}, got {formatted}"
                    })
        
        except pytz.NonExistentTimeError as e:
            # Check if error was expected
            if expected['error'] == 'NonExistentTimeError':
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"Expected NonExistentTimeError raised for {dt_str} in {zone}: {str(e)}"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Unexpected NonExistentTimeError for {dt_str} in {zone}: {str(e)}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_feature8():
    """Run all test cases for Feature 8."""
    print("Feature 8 Test Results:")
    print("======================")
    
    # Run all sub-tests
    all_results = []
    all_results.extend(test_unknown_timezone())
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
    success = test_feature8()
    sys.exit(0 if success else 1)