#!/usr/bin/env python3
"""
Debug script for test case 1.
"""

import sys
import os
import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz

# Test case 1: 2002-10-27 01:00:00, is_dst=True, delta_minutes=60
print("Test case 1:")
eastern = pytz.timezone('US/Eastern')
dt = datetime.datetime(2002, 10, 27, 1, 0, 0)
localized = eastern.localize(dt, is_dst=True)
print(f"Localized: {localized}")
print(f"Localized tzinfo: {localized.tzinfo}")
print(f"Localized utcoffset: {localized.utcoffset()}")
print(f"Localized dst: {localized.dst()}")
print(f"Localized tzname: {localized.tzname()}")

# Apply delta
delta = datetime.timedelta(minutes=60)
after_arithmetic = localized + delta
print(f"\nAfter arithmetic: {after_arithmetic}")
print(f"After arithmetic tzinfo: {after_arithmetic.tzinfo}")
print(f"After arithmetic utcoffset: {after_arithmetic.utcoffset()}")
print(f"After arithmetic dst: {after_arithmetic.dst()}")
print(f"After arithmetic tzname: {after_arithmetic.tzname()}")

# Convert to UTC
utc_dt = after_arithmetic.astimezone(pytz.UTC)
print(f"\nUTC: {utc_dt}")
print(f"UTC naive: {utc_dt.replace(tzinfo=None)}")

# What does normalize do?
normalized = eastern.normalize(after_arithmetic)
print(f"\nNormalized: {normalized}")
print(f"Normalized tzinfo: {normalized.tzinfo}")
print(f"Normalized utcoffset: {normalized.utcoffset()}")
print(f"Normalized dst: {normalized.dst()}")
print(f"Normalized tzname: {normalized.tzname()}")