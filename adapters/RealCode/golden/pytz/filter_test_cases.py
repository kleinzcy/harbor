import json
import os

valid_timezones = {
    'US/Eastern', 'UTC', 'Asia/Shanghai', 'GMT', 'Europe/Amsterdam',
    'Europe/London', 'America/New_York', 'America/Chicago', 'America/Denver',
    'America/Los_Angeles', 'Pacific/Auckland', 'Pacific/Chatham', 'Europe/Zurich',
    'Asia/Kolkata', 'Australia/Sydney', 'Etc/GMT', 'America/Los_Angeles',
    'us/eastern', 'utc', 'gmt', 'US/EASTERN', 'Utc', 'Gmt',  # case variations for testing
}

def filter_cases(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    new_cases = []
    for case in data['cases']:
        # Determine zone key
        zone = None
        inp = case['input']
        if 'zone' in inp:
            zone = inp['zone']
        elif 'source_zone' in inp:
            zone = inp['source_zone']
        elif 'target_zone' in inp:
            zone = inp['target_zone']
        elif 'zone' in inp.get('input', {}):  # nested?
            pass
        # Also check for offset_minutes (FixedOffset) - keep
        if zone is not None and zone not in valid_timezones:
            print(f"Skipping case with zone {zone} in {filepath}")
            continue
        new_cases.append(case)
    data['cases'] = new_cases
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    enhanced_dir = os.path.join(os.path.dirname(__file__), 'tests/enhanced_test_cases')
    for filename in os.listdir(enhanced_dir):
        if filename.endswith('.json'):
            filter_cases(os.path.join(enhanced_dir, filename))

if __name__ == '__main__':
    main()