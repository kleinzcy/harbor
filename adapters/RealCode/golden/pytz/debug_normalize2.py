#!/usr/bin/env python3
"""
Debug script for normalization issue.
"""

import sys
import os
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

# Test case 1
print("=== Test Case 1 ===")
tz = pytz.timezone('US/Eastern')
dt = datetime.datetime(2002, 10, 27, 1, 0, 0)
localized = tz.localize(dt, is_dst=True)
print(f"Start: {format_datetime(localized)}")
print(f"UTC equivalent: {localized.astimezone(pytz.utc)}")

# Add 60 minutes
after_arithmetic = localized + datetime.timedelta(minutes=60)
print(f"After +60 minutes: {format_datetime(after_arithmetic)}")
print(f"UTC equivalent: {after_arithmetic.astimezone(pytz.utc)}")

# Normalize
normalized = tz.normalize(after_arithmetic)
print(f"After normalize: {format_datetime(normalized)}")
print(f"UTC equivalent: {normalized.astimezone(pytz.utc)}")

print()

# Test case 2
print("=== Test Case 2 ===")
tz = pytz.timezone('US/Eastern')
dt = datetime.datetime(2002, 4, 7, 1, 0, 0)
localized = tz.localize(dt)
print(f"Start: {format_datetime(localized)}")
print(f"UTC equivalent: {localized.astimezone(pytz.utc)}")

# Add 60 minutes
after_arithmetic = localized + datetime.timedelta(minutes=60)
print(f"After +60 minutes: {format_datetime(after_arithmetic)}")
print(f"UTC equivalent: {after_arithmetic.astimezone(pytz.utc)}")

# Normalize
normalized = tz.normalize(after_arithmetic)
print(f"After normalize: {format_datetime(normalized)}")
print(f"UTC equivalent: {normalized.astimezone(pytz.utc)}")