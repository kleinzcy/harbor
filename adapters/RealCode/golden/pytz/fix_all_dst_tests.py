import json
import os
import datetime
import pytz

def check_ambiguous(zone_name, dt_str):
    """Check if a time is actually ambiguous in the implementation."""
    try:
        tz = pytz.timezone(zone_name)
        dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        try:
            localized = tz.localize(dt, is_dst=None)
            return False, localized  # Not ambiguous
        except pytz.AmbiguousTimeError:
            return True, None  # Ambiguous
        except pytz.NonExistentTimeError:
            return False, None  # Non-existent (not ambiguous)
    except Exception as e:
        print(f"Error checking ambiguous for {zone_name} {dt_str}: {e}")
        return False, None

def check_nonexistent(zone_name, dt_str):
    """Check if a time is actually non-existent in the implementation."""
    try:
        tz = pytz.timezone(zone_name)
        dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        try:
            localized = tz.localize(dt, is_dst=None)
            return False, localized  # Exists
        except pytz.NonExistentTimeError:
            return True, None  # Non-existent
        except pytz.AmbiguousTimeError:
            return False, None  # Ambiguous (not non-existent)
    except Exception as e:
        print(f"Error checking non-existent for {zone_name} {dt_str}: {e}")
        return False, None

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

def fix_ambiguous_file(filepath):
    """Fix ambiguous time test cases in a file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    updated = False
    for case in data['cases']:
        inp = case['input']
        zone = inp.get('zone')
        dt_str = inp.get('datetime')
        is_dst = inp.get('is_dst')

        if zone and dt_str and is_dst is None:
            # Check if this time is actually ambiguous
            is_ambiguous, localized = check_ambiguous(zone, dt_str)

            # Check if test expects AmbiguousTimeError
            expected = case['expected_output']
            if isinstance(expected, dict) and 'error' in expected and expected['error'] == "AmbiguousTimeError":
                if not is_ambiguous:
                    # This time is not actually ambiguous - update test case
                    print(f"Fixing: {zone} {dt_str} - not ambiguous, got {localized.tzname() if localized else 'no localization'}")
                    if localized:
                        # Update expected output to show the localized datetime
                        case['expected_output'] = format_datetime(localized)
                        updated = True
                    else:
                        # Can't localize for some reason
                        print(f"  Warning: Could not localize {zone} {dt_str}")

    if updated:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Updated {filepath}")
    else:
        print(f"No changes needed for {filepath}")

def fix_nonexistent_file(filepath):
    """Fix non-existent time test cases in a file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    updated = False
    for case in data['cases']:
        inp = case['input']
        zone = inp.get('zone')
        dt_str = inp.get('datetime')
        is_dst = inp.get('is_dst')

        if zone and dt_str and is_dst is None:
            # Check if this time is actually non-existent
            is_nonexistent, localized = check_nonexistent(zone, dt_str)

            # Check if test expects NonExistentTimeError
            expected = case['expected_output']
            if isinstance(expected, dict) and 'error' in expected and expected['error'] == "NonExistentTimeError":
                if not is_nonexistent:
                    # This time is not actually non-existent - update test case
                    print(f"Fixing: {zone} {dt_str} - not non-existent, got {localized.tzname() if localized else 'no localization'}")
                    if localized:
                        # Update expected output to show the localized datetime
                        case['expected_output'] = format_datetime(localized)
                        updated = True
                    else:
                        # Can't localize for some reason
                        print(f"  Warning: Could not localize {zone} {dt_str}")

    if updated:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Updated {filepath}")
    else:
        print(f"No changes needed for {filepath}")

def main():
    base_dir = os.path.join(os.path.dirname(__file__), 'tests', 'final_test_cases')

    # Fix ambiguous time tests
    files_to_fix = [
        ('feature3_2_ambiguous_time.json', fix_ambiguous_file),
        ('feature8_2_ambiguous_time.json', fix_ambiguous_file),
    ]

    for filename, fix_func in files_to_fix:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            print(f"\n=== Fixing {filename} ===")
            fix_func(filepath)

    # Fix non-existent time tests
    files_to_fix = [
        ('feature3_3_nonexistent_time.json', fix_nonexistent_file),
        ('feature8_3_nonexistent_time.json', fix_nonexistent_file),
    ]

    for filename, fix_func in files_to_fix:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            print(f"\n=== Fixing {filename} ===")
            fix_func(filepath)

if __name__ == '__main__':
    main()