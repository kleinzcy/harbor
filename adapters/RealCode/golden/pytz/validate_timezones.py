import pytz
import datetime

# Test if a time is ambiguous in a timezone
def test_ambiguous(zone_name, dt_str):
    try:
        tz = pytz.timezone(zone_name)
        dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        # Try to localize with is_dst=None
        try:
            localized = tz.localize(dt, is_dst=None)
            print(f"{zone_name} {dt_str}: NOT ambiguous (got {localized.tzname()})")
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

# Test if a time is non-existent in a timezone
def test_nonexistent(zone_name, dt_str):
    try:
        tz = pytz.timezone(zone_name)
        dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        try:
            localized = tz.localize(dt, is_dst=None)
            print(f"{zone_name} {dt_str}: EXISTS (got {localized.tzname()})")
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

# Test cases from our enhanced tests
print("=== Testing ambiguous times ===")
test_cases = [
    ("Europe/London", "2002-10-27 01:30:00"),
    ("Pacific/Auckland", "2002-04-07 02:30:00"),
]

for zone, dt in test_cases:
    test_ambiguous(zone, dt)

print("\n=== Testing non-existent times ===")
test_cases = [
    ("Europe/London", "2002-03-31 01:30:00"),
    ("Pacific/Auckland", "2002-10-27 02:30:00"),
]

for zone, dt in test_cases:
    test_nonexistent(zone, dt)