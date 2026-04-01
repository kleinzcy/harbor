#!/usr/bin/env python3
"""
Test script for Feature 5: Timezone Conversion
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


def test_utc_conversion():
    """Test UTC to local timezone conversion."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature5_1_utc_conversion.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            utc_dt_str = input_data['utc_datetime']
            target_zone = input_data['target_zone']
            expected = test_case['expected_output']
            
            # Parse UTC datetime
            utc_dt = parse_datetime(utc_dt_str)
            
            # Make it UTC-aware
            utc_aware = utc_dt.replace(tzinfo=pytz.UTC)
            
            # Get target timezone
            target_tz = pytz.timezone(target_zone)
            
            # Convert to target timezone
            converted = utc_aware.astimezone(target_tz)
            
            # Format result
            result = format_datetime(converted)
            
            # Check result
            if result == expected:
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"UTC conversion passed: {utc_dt_str} UTC -> {target_zone}"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"UTC conversion failed: expected {expected}, got {result}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_cross_timezone():
    """Test cross-timezone conversion."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature5_2_cross_timezone.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            source_zone = input_data['source_zone']
            source_dt_str = input_data['source_datetime']
            target_zone = input_data['target_zone']
            expected = test_case['expected_output']
            
            # Parse source datetime
            source_dt = parse_datetime(source_dt_str)
            
            # Get source timezone
            source_tz = pytz.timezone(source_zone)
            
            # Localize source datetime
            # Note: for simplicity, we don't specify is_dst here
            source_aware = source_tz.localize(source_dt)
            
            # Get target timezone
            target_tz = pytz.timezone(target_zone)
            
            # Convert to target timezone
            converted = source_aware.astimezone(target_tz)
            
            # Format result
            result = format_datetime(converted)
            
            # Check result
            if result == expected:
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"Cross-timezone conversion passed: {source_dt_str} {source_zone} -> {target_zone}"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Cross-timezone conversion failed: expected {expected}, got {result}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    return results


def test_feature5():
    """Run all test cases for Feature 5."""
    print("Feature 5 Test Results:")
    print("======================")
    
    # Run all sub-tests
    all_results = []
    all_results.extend(test_utc_conversion())
    all_results.extend(test_cross_timezone())
    
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
    success = test_feature5()
    sys.exit(0 if success else 1)