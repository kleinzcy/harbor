import json

def add_cases(filepath, new_cases):
    with open(filepath, 'r') as f:
        data = json.load(f)
    data['cases'].extend(new_cases)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# Feature 1
path1 = 'tests/enhanced_test_cases/feature1_basic_parametrization.json'
new1 = [
    # single argname with single argvalue
    {
        "input": {
            "argnames": "x",
            "argvalues": [5]
        },
        "expected_output": {
            "generated_methods": ["test_single_0"],
            "parameters": [{"x": 5}]
        }
    },
    # large number of parameter sets (10)
    {
        "input": {
            "argnames": "value",
            "argvalues": [[i] for i in range(10)]
        },
        "expected_output": {
            "generated_methods": [f"test_large_{i}" for i in range(10)],
            "parameters": [{"value": i} for i in range(10)]
        }
    },
    # argnames with tabs and newlines
    {
        "input": {
            "argnames": "x\t,\ty",
            "argvalues": [[1, 2], [3, 4]]
        },
        "expected_output": {
            "generated_methods": ["test_tabs_0", "test_tabs_1"],
            "parameters": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        }
    },
    # argnames with special characters (allowed)
    {
        "input": {
            "argnames": "x-y,z_w",
            "argvalues": [[1, 2], [3, 4]]
        },
        "expected_output": {
            "generated_methods": ["test_special_0", "test_special_1"],
            "parameters": [{"x-y": 1, "z_w": 2}, {"x-y": 3, "z_w": 4}]
        }
    },
    # empty argnames string (error)
    {
        "input": {
            "argnames": "",
            "argvalues": []
        },
        "expected_output": {
            "error": "Argument name at index 0 is empty after stripping"
        }
    },
    # duplicate argnames (allowed, omit parameters)
    {
        "input": {
            "argnames": "x,x",
            "argvalues": [[1, 2], [3, 4]]
        },
        "expected_output": {
            "generated_methods": ["test_dup_0", "test_dup_1"]
        }
    },
    # mixed types
    {
        "input": {
            "argnames": "value",
            "argvalues": [None, 3.14, "hello", True, False, {"key": "val"}, [1,2]]
        },
        "expected_output": {
            "generated_methods": [f"test_mixed_{i}" for i in range(7)]
        }
    }
]
add_cases(path1, new1)

# Feature 2
path2 = 'tests/enhanced_test_cases/feature2_custom_ids.json'
new2 = [
    # ids with None values mixed
    {
        "input": {
            "argnames": "x",
            "argvalues": [[1], [2], [3]],
            "ids": ["one", None, "three"]
        },
        "expected_output": {
            "generated_methods": ["test_with_ids_one", "test_with_ids_1", "test_with_ids_three"]
        }
    },
    # param object with id=None explicit
    {
        "input": {
            "argnames": "x",
            "argvalues": [{"__type__": "param", "args": [1], "id": None}]
        },
        "expected_output": {
            "generated_methods": ["test_with_ids_0"]
        }
    },
    # param object without id key
    {
        "input": {
            "argnames": "x",
            "argvalues": [{"__type__": "param", "args": [1]}]
        },
        "expected_output": {
            "generated_methods": ["test_with_ids_0"]
        }
    },
    # IDs with Unicode characters (invalid)
    {
        "input": {
            "argnames": "x",
            "argvalues": [[1]],
            "ids": ["café"]
        },
        "expected_output": {
            "error": "Invalid param id"
        }
    },
    # IDs with leading number (invalid)
    {
        "input": {
            "argnames": "x",
            "argvalues": [[1]],
            "ids": ["123abc"]
        },
        "expected_output": {
            "error": "Invalid param id"
        }
    },
    # IDs with underscore allowed
    {
        "input": {
            "argnames": "x",
            "argvalues": [[1], [2]],
            "ids": ["_hidden", "normal_123"]
        },
        "expected_output": {
            "generated_methods": ["test_with_ids__hidden", "test_with_ids_normal_123"]
        }
    },
    # Empty string ID becomes None
    {
        "input": {
            "argnames": "x",
            "argvalues": [[1]],
            "ids": [""]
        },
        "expected_output": {
            "generated_methods": ["test_with_ids_0"]
        }
    }
]
add_cases(path2, new2)

# Feature 3
path3 = 'tests/enhanced_test_cases/feature3_async_support.json'
new3 = [
    # async with ids
    {
        "input": {
            "argnames": "x",
            "argvalues": [[1], [2]],
            "ids": ["one", "two"],
            "async": True
        },
        "expected_output": {
            "generated_methods": ["test_async_method_one", "test_async_method_two"],
            "async": True
        }
    },
    # async with param objects
    {
        "input": {
            "argnames": "x",
            "argvalues": [
                {"__type__": "param", "args": [1], "id": "first"},
                {"__type__": "param", "args": [2], "id": "second"}
            ],
            "async": True
        },
        "expected_output": {
            "generated_methods": ["test_async_method_first", "test_async_method_second"],
            "async": True
        }
    },
    # async with empty argvalues
    {
        "input": {
            "argnames": "x",
            "argvalues": [],
            "async": True
        },
        "expected_output": {
            "generated_methods": [],
            "async": True
        }
    }
]
add_cases(path3, new3)

# Feature 4.1
path4_1 = 'tests/enhanced_test_cases/feature4_1_decorator_constraints.json'
new4_1 = [
    # decorator ordering with @unittest.skip
    {
        "input": {
            "scenario": "parametrize with unittest.skip",
            "decorators": ["@unittest.skip", "@parametrize"]
        },
        "expected_output": {
            "error": "@parametrize must be the top-most decorator"
        }
    },
    # decorator ordering with @unittest.expectedFailure
    {
        "input": {
            "scenario": "parametrize with expectedFailure",
            "decorators": ["@unittest.expectedFailure", "@parametrize"]
        },
        "expected_output": {
            "error": "@parametrize must be the top-most decorator"
        }
    }
]
add_cases(path4_1, new4_1)

# Feature 4.2
path4_2 = 'tests/enhanced_test_cases/feature4_2_parameter_validation.json'
new4_2 = [
    # nested sequences as parameter values
    {
        "input": {
            "argnames": "a,b",
            "argvalues": [[[1,2], "hello"], [[3,4], "world"]]
        },
        "expected_output": {
            "generated_methods": ["test_nested_0", "test_nested_1"]
        }
    },
    # param object with wrong length error
    {
        "input": {
            "argnames": "x,y",
            "argvalues": [{"__type__": "param", "args": [1]}]
        },
        "expected_output": {
            "error": "param object at index 0 has wrong number of arguments"
        }
    },
    # single value for multiple argnames error
    {
        "input": {
            "argnames": "x,y",
            "argvalues": [1]
        },
        "expected_output": {
            "error": "argvalue at index 0 is not a tuple or param instance"
        }
    },
    # dict as single value error (already covered but duplicate)
]
add_cases(path4_2, new4_2)

# Feature 4.3
path4_3 = 'tests/enhanced_test_cases/feature4_3_error_enhancement.json'
new4_3 = [
    # error enhancement for async failures
    {
        "input": {
            "python_version": "3.11",
            "argnames": "x,expected",
            "argvalues": [[1, 2]],
            "test_assertion": "self.assertEqual(x**2, expected)",
            "async": True
        },
        "expected_output": {
            "error_contains": "Test parameters: x=1, expected=2"
        }
    },
    # multiple failures (still only first note)
    {
        "input": {
            "python_version": "3.11",
            "argnames": "x,expected",
            "argvalues": [[1, 2], [3, 8]],
            "test_assertion": "self.assertEqual(x**2, expected)"
        },
        "expected_output": {
            "error_contains": "Test parameters: x=1, expected=2"
        }
    }
]
add_cases(path4_3, new4_3)

# Feature 4.4
path4_4 = 'tests/enhanced_test_cases/feature4_4_compatibility.json'
new4_4 = [
    # mixed test suite with different prefixes
    {
        "input": {
            "test_class": "MixedPrefix",
            "methods": ["test_one", "@parametrize test_two", "test_three"]
        },
        "expected_output": {
            "runs_with": ["unittest", "pytest", "Django"],
            "non_parametrized_work": True
        }
    },
    # empty argvalues with single argname (already covered)
]
add_cases(path4_4, new4_4)

print("Enhanced all test cases.")