# unittest-parametrize - unittest test parameterization library

## Project Goal

Build a Python library that provides parameterized testing capabilities for the unittest framework, allowing developers to write data-driven tests with minimal boilerplate code without manually creating multiple test methods or using loops. The library will offer a decorator-based API similar to pytest.mark.parametrize, automatically generating independent test methods for each parameter set, supporting both synchronous and asynchronous tests, and providing flexible configuration options for custom test IDs and parameter formats.

---

## Background & Problem

Without this library, developers using unittest are forced to either write repetitive test methods for each test case or use loops within test methods, which obscures test reporting and makes debugging difficult. This leads to code duplication, reduced test readability, maintenance overhead when adding new test cases, and inability to leverage test runners' built-in features for individual test cases (like selective test execution, parallelization, and detailed failure reporting).

With this library, developers can define test parameters declaratively using a simple decorator, automatically generating separate test methods for each parameter set. This enables clear test reporting, easy debugging with parameter-specific failure information, and seamless integration with existing unittest infrastructure while maintaining full compatibility with test runners like pytest and Django's test framework.

---

## Core Features

### Feature 1: Core Parameterization Decorator

**As a developer**, I want to apply a `@parametrize` decorator to my test methods, so I can automatically generate multiple independent test cases from a single method definition.

**Expected Behavior / Usage:**

The `@parametrize` decorator accepts `argnames` (string or sequence of strings) and `argvalues` (sequence of tuples or `param` objects). When applied to a test method in a class inheriting from `ParametrizedTestCase`, the decorator replaces the original method with multiple generated methods, each receiving one set of parameters. The generated methods are named with suffixes (`_0`, `_1`, etc.) or custom IDs. The decorator supports both string-form parameter names (e.g., `"x,expected"`) and tuple-form (e.g., `("x", "expected")`), automatically cleaning whitespace.

**Test Cases:** `tests/test_cases/feature1_basic_parametrization.json`

```json
{
    "description": "Basic parameterization with string and tuple argument names",
    "cases": [
        {
            "input": {"argnames": "x,expected", "argvalues": [[1, 1], [2, 4], [3, 9]]},
            "expected_output": {"generated_methods": ["test_square_0", "test_square_1", "test_square_2"], "parameters": [{"x": 1, "expected": 1}, {"x": 2, "expected": 4}, {"x": 3, "expected": 9}]}
        },
        {
            "input": {"argnames": ["x", "expected"], "argvalues": [[1, 1], [2, 4]]},
            "expected_output": {"generated_methods": ["test_square_0", "test_square_1"], "parameters": [{"x": 1, "expected": 1}, {"x": 2, "expected": 4}]}
        },
        {
            "input": {"argnames": "x, expected", "argvalues": [[1, 1], [2, 4]]},
            "expected_output": {"generated_methods": ["test_with_spaces_0", "test_with_spaces_1"], "parameters": [{"x": 1, "expected": 1}, {"x": 2, "expected": 4}]}
        }
    ]
}
```

---

### Feature 2: Custom Test ID Support

**As a developer**, I want to assign custom identifiers to parameterized tests, so I can have meaningful test names that improve readability and debugging.

**Expected Behavior / Usage:**

Custom IDs can be provided via the `ids` parameter (list/sequence or callable) or embedded within `param` objects. The IDs are used as suffixes for generated test method names. IDs must be valid Python identifier suffixes (alphanumeric plus underscores, not starting with a number). Duplicate IDs are detected and rejected. When `ids` is a callable, it is invoked for each parameter value (or each element of a tuple) and the results are joined with underscores.

**Test Cases:** `tests/test_cases/feature2_custom_ids.json`

```json
{
    "description": "Custom test IDs via ids parameter and param objects",
    "cases": [
        {
            "input": {"argnames": "value,expected", "argvalues": [[1, 1], [2, 4], [3, 9]], "ids": ["one", "two", "three"]},
            "expected_output": {"generated_methods": ["test_with_ids_one", "test_with_ids_two", "test_with_ids_three"]}
        },
        {
            "input": {"argnames": "input,output", "argvalues": [{"__type__": "param", "args": ["hello", 5], "id": "string"}, {"__type__": "param", "args": [[1, 2, 3], 3], "id": "list"}, {"__type__": "param", "args": [{}, 0], "id": "empty"}]},
            "expected_output": {"generated_methods": ["test_length_string", "test_length_list", "test_length_empty"]}
        },
        {
            "input": {"argnames": "x,expected", "argvalues": [[1, 1], [2, 4]], "ids": ["same", "same"]},
            "expected_output": {"error": "Duplicate param id 'same'"}
        }
    ]
}
```

---

### Feature 3: Async Test Support

**As a developer**, I want to parameterize asynchronous test methods (async def), so I can write data-driven async tests that work with Python's asyncio.

**Expected Behavior / Usage:**

The decorator automatically detects coroutine functions via `inspect.iscoroutinefunction()` and generates appropriate async test methods. Parameterized async tests can be combined with `IsolatedAsyncioTestCase` for proper event loop handling. The generated async methods preserve the async nature and can use await expressions.

**Test Cases:** `tests/test_cases/feature3_async_support.json`

```json
{
    "description": "Parameterization of asynchronous test methods",
    "cases": [
        {
            "input": {"argnames": "delay,multiplier", "argvalues": [[0.001, 2], [0.002, 3], [0.003, 4]], "async": true},
            "expected_output": {"generated_methods": ["test_async_operation_0", "test_async_operation_1", "test_async_operation_2"], "async": true}
        },
        {
            "input": {"argnames": "value", "argvalues": [[0], [1], [2]], "async": true},
            "expected_output": {"generated_methods": ["test_async_values_0", "test_async_values_1", "test_async_values_2"], "async": true}
        }
    ]
}
```

---

### Feature 4: Advanced Configuration & Integration

**As a developer**, I want robust validation, error reporting, and seamless integration with the unittest ecosystem, so I can use the library reliably in real-world projects.

**Expected Behavior / Usage:**

The library must enforce proper usage patterns, validate inputs comprehensively, enhance debugging experience, and maintain full compatibility with the unittest ecosystem.

*4.1 Decorator Constraints & Validation —* The `@parametrize` decorator must be the outermost decorator on a test method; stacking multiple `@parametrize` decorators is prohibited. Duplicate generated method names are detected. Clear error messages are provided for misconfiguration.

**Test Cases:** `tests/test_cases/feature4_1_decorator_constraints.json`

```json
{
    "description": "Decorator ordering and stacking validation",
    "cases": [
        {
            "input": {"scenario": "parametrize not outermost", "decorators": ["@mock.patch", "@parametrize"]},
            "expected_output": {"error": "@parametrize must be the top-most decorator"}
        },
        {
            "input": {"scenario": "multiple parametrize decorators", "decorators": ["@parametrize", "@parametrize"]},
            "expected_output": {"error": "@parametrize cannot be stacked"}
        },
        {
            "input": {"scenario": "duplicate generated method name", "existing_method": "test_something_0", "parametrize_method": "test_something"},
            "expected_output": {"error": "Duplicate test name 'test_something_0'"}
        }
    ]
}
```

*4.2 Parameter Validation & Type Checking —* Validates that the number of argument names matches each tuple's length, ensures argvalues are tuples or param objects (or single values when single argname), and checks that parameter names match the function signature.

**Test Cases:** `tests/test_cases/feature4_2_parameter_validation.json`

```json
{
    "description": "Parameter validation and type checking",
    "cases": [
        {
            "input": {"argnames": "x,y", "argvalues": [[1]]},
            "expected_output": {"error": "tuple at index 0 has wrong number of arguments (1 != 2)"}
        },
        {
            "input": {"argnames": "x", "argvalues": [{"x": 1}]},
            "expected_output": {"error": "argvalue at index 0 is not a tuple or param instance"}
        },
        {
            "input": {"argnames": "x", "argvalues": [1, 2, 3]},
            "expected_output": {"generated_methods": ["test_single_values_0", "test_single_values_1", "test_single_values_2"]}
        }
    ]
}
```

*4.3 Error Enhancement & Debugging —* In Python 3.11+, failed parameterized tests automatically include parameter values in the error message via `exc.add_note()`. This improves debugging by showing which parameter set caused the failure.

**Test Cases:** `tests/test_cases/feature4_3_error_enhancement.json`

```json
{
    "description": "Enhanced error messages in Python 3.11+",
    "cases": [
        {
            "input": {"python_version": "3.11", "argnames": "x,expected", "argvalues": [[1, 2], [3, 8]], "test_assertion": "self.assertEqual(x**2, expected)"},
            "expected_output": {"error_contains": "Test parameters: x=1, expected=2"}
        }
    ]
}
```

*4.4 Compatibility & Integration —* The `ParametrizedTestCase` base class inherits from `unittest.TestCase` and works with standard unittest runners, pytest, and Django's test framework. Non-parameterized test methods in the same class continue to work normally.

**Test Cases:** `tests/test_cases/feature4_4_compatibility.json`

```json
{
    "description": "Compatibility with unittest ecosystem",
    "cases": [
        {
            "input": {"test_class": "MixedTestSuite", "methods": ["test_traditional", "@parametrize test_parametrized", "test_another_traditional"]},
            "expected_output": {"runs_with": ["unittest", "pytest", "Django"], "non_parametrized_work": true}
        },
        {
            "input": {"argnames": "x", "argvalues": []},
            "expected_output": {"generated_methods": [], "original_method_removed": true}
        }
    ]
}
```

---

## Deliverables

The overall implementation should include:

1. **A Python library package** named `unittest_parametrize` installable via pip, with a complete `pyproject.toml` file declaring dependencies and package configuration. The library must export the core components: `parametrize` decorator, `ParametrizedTestCase` base class, and `param` parameter object, accessible via `from unittest_parametrize import parametrize, ParametrizedTestCase, param`.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible — any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_basic_parametrization.json` should write its output to `tests/stdout/feature1_basic_parametrization@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.