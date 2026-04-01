import pytz
import datetime

# Test if a time is ambiguous in US/Eastern
def test_ambiguous(zone_name, dt_str):
    try:
        tz = pytz.timezone(zone_name)
        dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        # Try to localize with is_dst=None
        try:
            localized = tz.localize(dt, is_dst=None)
            print(f"{zone_name} {dt_str}: NOT ambiguous (got {localized.tzname()} {localized.strftime('%z')})")
            return False
        except pytz.AmbiguousTimeError:
            print(f"{zone_name} {dt_str}: AMBIGUOUS ✓")
            return True
        except pytz.NonExistentTimeError:
            print(f"{zone_name} {dt_str}: NONEXISTENT (not ambiguous)")
            return False
    except Exception as e:
        print(f"{zone_name} {dt_str}: ERROR {e}")
        return False

# Test if a time is non-existent in US/Eastern
def test_nonexistent(zone_name, dt_str):
    try:
        tz = pytz.timezone(zone_name)
        dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        try:
            localized = tz.localize(dt, is_dst=None)
            print(f"{zone_name} {dt_str}: EXISTS (got {localized.tzname()} {localized.strftime('%z')})")
            return False
        except pytz.NonExistentTimeError:
            print(f"{zone_name} {dt_str}: NONEXISTENT ✓")
            return True
        except pytz.AmbiguousTimeError:
            print(f"{zone_name} {dt_str}: AMBIGUOUS (not nonexistent)")
            return False
    except Exception as e:
        print(f"{zone_name} {dt_str}: ERROR {e}")
        return False

# Test cases from feature8 error handling tests
print("=== Testing ambiguous times for US/Eastern ===")
test_cases = [
    ("US/Eastern", "2002-10-27 01:30:00"),
    ("US/Eastern", "2002-10-27 01:00:00"),
    ("US/Eastern", "2002-10-27 06:00:00"),  # Should not be ambiguous
]

for zone, dt in test_cases:
    test_ambiguous(zone, dt)

print("\n=== Testing non-existent times for US/Eastern ===")
test_cases = [
    ("US/Eastern", "2002-04-07 02:30:00"),
    ("US/Eastern", "2002-04-07 02:00:00"),
    ("US/Eastern", "2002-04-07 03:00:00"),  # Should not be non-existent
]

for zone, dt in test_cases:
    test_nonexistent(zone, dt)

# Let's also test some other times to understand DST transitions
print("\n=== Testing DST transition times for US/Eastern ===")
# Spring forward: Clocks go from 1:59:59 EST to 3:00:00 EDT
# Test times around the transition
transition_times = [
    ("US/Eastern", "2002-04-07 01:59:59"),
    ("US/Eastern", "2002-04-07 02:00:00"),
    ("US/Eastern", "2002-04-07 02:30:00"),
    ("US/Eastern", "2002-04-07 02:59:59"),
    ("US/Eastern", "2002-04-07 03:00:00"),
    ("US/Eastern", "2002-04-07 03:30:00"),
]

for zone, dt in transition_times:
    test_nonexistent(zone, dt)

# Fall back: Clocks go from 1:59:59 EDT back to 1:00:00 EST
# Test times around the transition
print("\n=== Testing fall-back transition for US/Eastern ===")
transition_times = [
    ("US/Eastern", "2002-10-27 00:59:59"),
    ("US/Eastern", "2002-10-27 01:00:00"),
    ("US/Eastern", "2002-10-27 01:30:00"),
    ("US/Eastern", "2002-10-27 01:59:59"),
    ("US/Eastern", "2002-10-27 02:00:00"),
    ("US/Eastern", "2002-10-27 02:30:00"),
]

for zone, dt in transition_times:
    test_ambiguous(zone, dt)