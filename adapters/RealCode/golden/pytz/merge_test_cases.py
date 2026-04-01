import json
import os

def merge_test_cases(original_file, enhanced_file, output_file):
    with open(original_file, 'r') as f:
        original = json.load(f)
    with open(enhanced_file, 'r') as f:
        enhanced = json.load(f)

    # Create set of existing inputs to avoid duplicates
    existing_inputs = set()
    for case in original['cases']:
        # Convert input dict to string for comparison
        existing_inputs.add(json.dumps(case['input'], sort_keys=True))

    # Add enhanced cases that aren't duplicates
    for case in enhanced['cases']:
        input_str = json.dumps(case['input'], sort_keys=True)
        if input_str not in existing_inputs:
            original['cases'].append(case)
            existing_inputs.add(input_str)

    with open(output_file, 'w') as f:
        json.dump(original, f, indent=2)

def main():
    base_dir = os.path.join(os.path.dirname(__file__), 'tests')
    test_cases_dir = os.path.join(base_dir, 'test_cases')
    enhanced_dir = os.path.join(base_dir, 'enhanced_test_cases')
    final_dir = os.path.join(base_dir, 'final_test_cases')

    os.makedirs(final_dir, exist_ok=True)

    for filename in os.listdir(test_cases_dir):
        if filename.endswith('.json'):
            original = os.path.join(test_cases_dir, filename)
            enhanced = os.path.join(enhanced_dir, filename)
            output = os.path.join(final_dir, filename)

            if os.path.exists(enhanced):
                merge_test_cases(original, enhanced, output)
                print(f"Merged {filename}")
            else:
                import shutil
                shutil.copy(original, output)
                print(f"Copied {filename} (no enhanced version)")

if __name__ == '__main__':
    main()