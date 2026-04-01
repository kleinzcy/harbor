#!/usr/bin/env python3
"""
Test script for Feature 4: Timezone Normalization
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


def test_feature4():
    """Run all test cases for Feature 4."""
    # Load test cases
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature4_normalization.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    results = []
    
    for i, test_case in enumerate(test_data['cases']):
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            delta_minutes = input_data['delta_minutes']
            is_dst = input_data.get('is_dst')
            expected = test_case['expected_output']
            
            # Parse datetime
            dt = parse_datetime(dt_str)
            
            # Get timezone
            tz = pytz.timezone(zone)
            
            # Localize datetime
            if is_dst is not None:
                localized = tz.localize(dt, is_dst=is_dst)
            else:
                localized = tz.localize(dt)
            
            # Apply time delta
            delta = datetime.timedelta(minutes=delta_minutes)
            after_arithmetic = localized + delta
            
            # Get before normalization result
            before_normalize = format_datetime(after_arithmetic)
            
            # Normalize
            normalized = tz.normalize(after_arithmetic)
            
            # Get after normalization result
            after_normalize = format_datetime(normalized)
            
            # Check results
            if before_normalize == expected['before_normalize'] and after_normalize == expected['after_normalize']:
                results.append({
                    'case': i,
                    'status': 'PASS',
                    'message': f"Normalization passed for {dt_str} in {zone} with delta {delta_minutes} minutes"
                })
            else:
                results.append({
                    'case': i,
                    'status': 'FAIL',
                    'message': f"Normalization failed: before expected {expected['before_normalize']}, got {before_normalize}; after expected {expected['after_normalize']}, got {after_normalize}"
                })
        
        except Exception as e:
            results.append({
                'case': i,
                'status': 'ERROR',
                'message': f"Test execution error: {type(e).__name__}: {str(e)}"
            })
    
    # Print summary
    print("Feature 4 Test Results:")
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
    success = test_feature4()
    sys.exit(0 if success else 1)