#!/usr/bin/env python3
"""
Main test runner for all pytz features.
"""

import sys
import os
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test_module(module_name):
    """Run a test module and return results."""
    try:
        # Import the test module
        spec = importlib.util.spec_from_file_location(
            module_name, 
            os.path.join(os.path.dirname(__file__), f"{module_name}.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the test - each module has a test_featureX() function
        # Extract the feature number from module name
        feature_num = module_name.replace('test_feature', '')
        test_func_name = f"test_feature{feature_num}"
        
        if hasattr(module, test_func_name):
            return module.__dict__[test_func_name]()
        else:
            print(f"Error: {module_name} has no {test_func_name}() function")
            return False
    
    except Exception as e:
        print(f"Error running {module_name}: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Run all test modules."""
    print("Running all pytz tests")
    print("======================")
    print()
    
    # List of all test modules
    test_modules = [
        'test_feature1',  # Timezone Object Creation
        'test_feature2',  # Lazy Collections
        'test_feature3',  # Time Localization
        'test_feature4',  # Timezone Normalization
        'test_feature5',  # Timezone Conversion
        'test_feature6',  # Fixed Offset Timezone
        'test_feature7',  # Country Timezone Query
        'test_feature8',  # Error Handling and Exceptions
        'test_feature9',  # Timezone Serialization
        'test_feature10', # Timezone Collections and Metadata
    ]
    
    results = {}
    all_passed = True
    
    for module_name in test_modules:
        print(f"Running {module_name}...")
        success = run_test_module(module_name)
        results[module_name] = success
        if not success:
            all_passed = False
        print()
    
    # Print summary
    print("Test Summary")
    print("============")
    for module_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} {module_name}")
    
    print()
    if all_passed:
        print("All tests passed! ✅")
    else:
        print("Some tests failed. ❌")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)