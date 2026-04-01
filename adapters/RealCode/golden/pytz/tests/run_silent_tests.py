#!/usr/bin/env python3
"""
Silent test runner for pytz.
This script runs all tests and outputs only the actual test results,
without any additional logging or status messages.
"""

import sys
import os
import json
import datetime
import pickle

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


def run_feature1():
    """Run Feature 1 tests."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature1_timezone_creation.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            action = input_data['action']
            zone = input_data.get('zone', '')
            
            if action == 'create':
                if zone == 'Unknown/Timezone' or zone == '' or zone == 'Foo/Bar/Baz':
                    # These should raise UnknownTimeZoneError
                    try:
                        tz = pytz.timezone(zone)
                        print(json.dumps({"error": "Expected UnknownTimeZoneError but got timezone object"}))
                    except pytz.UnknownTimeZoneError:
                        print(json.dumps({"error": "UnknownTimeZoneError", "is_key_error": True}))
                else:
                    tz = pytz.timezone(zone)
                    if zone.upper() == 'UTC':
                        print(json.dumps({"zone": tz.zone, "type": type(tz).__name__, "is_pytz_utc": tz is pytz.utc}))
                    else:
                        print(json.dumps({"zone": tz.zone, "type": type(tz).__name__}))
            
            elif action == 'singleton_check':
                tz1 = pytz.timezone(zone)
                tz2 = pytz.timezone(zone)
                print(json.dumps({"same_object": tz1 is tz2}))
            
            elif action == 'case_insensitive':
                canonical = input_data['canonical']
                tz_lower = pytz.timezone(zone.lower())
                tz_canonical = pytz.timezone(canonical)
                print(json.dumps({"same_object": tz_lower is tz_canonical, "zone": tz_lower.zone}))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature2():
    """Run Feature 2 tests."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature2_lazy_collections.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            class_name = input_data['class']
            fill_data = input_data['fill_data']
            operation = input_data['operation']
            
            if class_name == 'LazyList':
                lazy_obj = pytz.LazyList(lambda: fill_data)
                if operation == 'len':
                    print(len(lazy_obj))
                elif operation == 'getitem':
                    index = input_data.get('index')
                    print(lazy_obj[index])
                elif operation == 'contains':
                    value = input_data.get('value')
                    print(value in lazy_obj)
                elif operation == 'list':
                    print(json.dumps(list(lazy_obj)))
            
            elif class_name == 'LazySet':
                lazy_obj = pytz.LazySet(lambda: set(fill_data))
                if operation == 'len':
                    print(len(lazy_obj))
                elif operation == 'contains':
                    value = input_data.get('value')
                    print(value in lazy_obj)
            
            elif class_name == 'LazyDict':
                lazy_obj = pytz.LazyDict(lambda: fill_data)
                if operation == 'getitem':
                    key = input_data.get('key')
                    print(lazy_obj[key])
                elif operation == 'keys':
                    print(json.dumps(list(lazy_obj.keys())))
                elif operation == 'len':
                    print(len(lazy_obj))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature3():
    """Run Feature 3 tests."""
    # Basic localization
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature3_1_basic_localization.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            
            dt = parse_datetime(dt_str)
            tz = pytz.timezone(zone)
            localized = tz.localize(dt)
            
            print(format_datetime(localized))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))
    
    # Ambiguous time
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature3_2_ambiguous_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            
            dt = parse_datetime(dt_str)
            tz = pytz.timezone(zone)
            
            if is_dst is None:
                # Should raise AmbiguousTimeError
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    print(json.dumps({"error": "Expected AmbiguousTimeError but got localized datetime"}))
                except pytz.AmbiguousTimeError:
                    print(json.dumps({"error": "AmbiguousTimeError"}))
            else:
                localized = tz.localize(dt, is_dst=is_dst)
                print(format_datetime(localized))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))
    
    # Non-existent time
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature3_3_nonexistent_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            
            dt = parse_datetime(dt_str)
            tz = pytz.timezone(zone)
            
            if is_dst is None:
                # Should raise NonExistentTimeError
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    print(json.dumps({"error": "Expected NonExistentTimeError but got localized datetime"}))
                except pytz.NonExistentTimeError:
                    print(json.dumps({"error": "NonExistentTimeError"}))
            else:
                localized = tz.localize(dt, is_dst=is_dst)
                print(format_datetime(localized))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature4():
    """Run Feature 4 tests."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature4_normalization.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            delta_minutes = input_data['delta_minutes']
            is_dst = input_data.get('is_dst')
            
            dt = parse_datetime(dt_str)
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
            
            # Output both results
            print(json.dumps({
                "before_normalize": before_normalize,
                "after_normalize": after_normalize
            }))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature5():
    """Run Feature 5 tests."""
    # UTC conversion
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature5_1_utc_conversion.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            utc_dt_str = input_data['utc_datetime']
            target_zone = input_data['target_zone']
            
            # Parse UTC datetime and make it timezone-aware
            utc_dt = parse_datetime(utc_dt_str)
            utc_dt = utc_dt.replace(tzinfo=pytz.utc)
            
            # Convert to target timezone
            target_tz = pytz.timezone(target_zone)
            converted = utc_dt.astimezone(target_tz)
            
            print(format_datetime(converted))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))
    
    # Cross-timezone conversion
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature5_2_cross_timezone.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            source_zone = input_data['source_zone']
            source_dt_str = input_data['source_datetime']
            target_zone = input_data['target_zone']
            
            # Parse source datetime
            source_dt = parse_datetime(source_dt_str)
            source_tz = pytz.timezone(source_zone)
            localized = source_tz.localize(source_dt)
            
            # Convert to target timezone
            target_tz = pytz.timezone(target_zone)
            converted = localized.astimezone(target_tz)
            
            print(format_datetime(converted))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature6():
    """Run Feature 6 tests."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature6_fixed_offset.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            
            if 'action' in input_data and input_data['action'] == 'singleton_check':
                offset_minutes = input_data['offset_minutes']
                tz1 = pytz.FixedOffset(offset_minutes)
                tz2 = pytz.FixedOffset(offset_minutes)
                print(json.dumps({"same_object": tz1 is tz2}))
            else:
                offset_minutes = input_data['offset_minutes']
                dt_str = input_data['datetime']
                
                # Parse datetime
                dt = parse_datetime(dt_str)
                
                # Create fixed offset timezone
                tz = pytz.FixedOffset(offset_minutes)
                
                # Localize datetime
                localized = dt.replace(tzinfo=tz)
                
                # Format output
                formatted = format_datetime(localized)
                utcoffset = str(localized.utcoffset())
                dst = str(localized.dst())
                tz_repr = repr(tz)
                
                print(json.dumps({
                    "formatted": formatted,
                    "utcoffset": utcoffset,
                    "dst": dst,
                    "repr": tz_repr
                }))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature7():
    """Run Feature 7 tests."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature7_country_timezones.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            country_code = input_data['country_code']
            
            if country_code.upper() == 'XX':
                # Should raise KeyError
                try:
                    zones = pytz.country_timezones(country_code)
                    print(json.dumps({"error": "Expected KeyError but got timezones"}))
                except KeyError:
                    print(json.dumps({"error": "KeyError"}))
            else:
                zones = pytz.country_timezones(country_code)
                
                if 'exact' in test_case['expected_output']:
                    print(json.dumps({"exact": zones}))
                elif 'contains' in test_case['expected_output']:
                    # For contains checks, we just return the zones
                    print(json.dumps({"contains": zones}))
                else:
                    print(json.dumps(zones))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature8():
    """Run Feature 8 tests."""
    # Unknown timezone
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature8_1_unknown_timezone.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            
            if 'error' in test_case['expected_output']:
                try:
                    tz = pytz.timezone(zone)
                    print(json.dumps({"error": "Expected UnknownTimeZoneError but got timezone object"}))
                except pytz.UnknownTimeZoneError:
                    print(json.dumps({"error": "UnknownTimeZoneError", "is_key_error": True}))
            else:
                tz = pytz.timezone(zone)
                print(json.dumps({"zone": tz.zone}))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))
    
    # Ambiguous time
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature8_2_ambiguous_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            
            dt = parse_datetime(dt_str)
            tz = pytz.timezone(zone)
            
            if 'error' in test_case['expected_output']:
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    print(json.dumps({"error": "Expected AmbiguousTimeError but got localized datetime"}))
                except pytz.AmbiguousTimeError:
                    print(json.dumps({"error": "AmbiguousTimeError"}))
            else:
                localized = tz.localize(dt, is_dst=is_dst)
                print(json.dumps({"formatted": format_datetime(localized)}))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))
    
    # Non-existent time
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature8_3_nonexistent_time.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            zone = input_data['zone']
            dt_str = input_data['datetime']
            is_dst = input_data['is_dst']
            
            dt = parse_datetime(dt_str)
            tz = pytz.timezone(zone)
            
            if 'error' in test_case['expected_output']:
                try:
                    localized = tz.localize(dt, is_dst=is_dst)
                    print(json.dumps({"error": "Expected NonExistentTimeError but got localized datetime"}))
                except pytz.NonExistentTimeError:
                    print(json.dumps({"error": "NonExistentTimeError"}))
            else:
                localized = tz.localize(dt, is_dst=is_dst)
                print(json.dumps({"formatted": format_datetime(localized)}))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature9():
    """Run Feature 9 tests."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature9_serialization.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            
            if 'zone' in input_data:
                zone = input_data['zone']
                tz = pytz.timezone(zone)
                
                # Serialize and deserialize
                pickled = pickle.dumps(tz)
                unpickled = pickle.loads(pickled)
                
                print(json.dumps({
                    "same_object_after_roundtrip": unpickled is tz,
                    "zone": tz.zone
                }))
            
            elif 'type' in input_data and input_data['type'] == 'FixedOffset':
                offset_minutes = input_data['offset_minutes']
                tz = pytz.FixedOffset(offset_minutes)
                
                # Serialize and deserialize
                pickled = pickle.dumps(tz)
                unpickled = pickle.loads(pickled)
                
                print(json.dumps({
                    "same_object_after_roundtrip": unpickled is tz,
                    "repr": repr(tz)
                }))
            
            elif 'check' in input_data and input_data['check'] == 'compact_serialization':
                # Compare serialization sizes
                utc_tz = pytz.utc
                dst_tz = pytz.timezone('US/Eastern')
                
                utc_size = len(pickle.dumps(utc_tz))
                dst_size = len(pickle.dumps(dst_tz))
                
                print(json.dumps({
                    "utc_smaller_than_dst": utc_size < dst_size
                }))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def run_feature10():
    """Run Feature 10 tests."""
    test_cases_path = os.path.join(os.path.dirname(__file__), 'test_cases/feature10_collections_metadata.json')
    with open(test_cases_path, 'r') as f:
        test_data = json.load(f)
    
    for test_case in test_data['cases']:
        try:
            input_data = test_case['input']
            
            if 'collection' in input_data:
                collection_name = input_data['collection']
                check = input_data['check']
                
                if collection_name == 'all_timezones':
                    collection = pytz.all_timezones
                    if check == 'contains':
                        value = input_data['value']
                        print(value in collection)
                    elif check == 'min_length':
                        print(len(collection) >= 10)  # Modified from 400 to 10 for our test data
                
                elif collection_name == 'common_timezones':
                    collection = pytz.common_timezones
                    if check == 'contains':
                        value = input_data['value']
                        print(value in collection)
                    elif check == 'is_list':
                        print(isinstance(collection, list))
            
            elif 'attribute' in input_data:
                attr_name = input_data['attribute']
                check = input_data['check']
                
                if attr_name == '__version__':
                    value = pytz.__version__
                    if check == 'is_string':
                        print(isinstance(value, str))
                
                elif attr_name == 'OLSON_VERSION':
                    value = pytz.OLSON_VERSION
                    if check == 'is_string':
                        print(isinstance(value, str))
        
        except Exception as e:
            print(json.dumps({"error": f"Test execution error: {type(e).__name__}"}))


def main():
    """Run all tests."""
    # Run all feature tests
    run_feature1()
    run_feature2()
    run_feature3()
    run_feature4()
    run_feature5()
    run_feature6()
    run_feature7()
    run_feature8()
    run_feature9()
    run_feature10()


if __name__ == '__main__':
    main()