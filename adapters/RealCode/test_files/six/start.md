# Six - Python 2/3 Compatibility Library

## Project Goal

Build a lightweight Python library that allows developers to write **one codebase** that runs on both Python 2.7 and Python 3.3+ without writing version checks everywhere.

---

## Background & Problem

Without this library, developers are forced to manually detect the Python version at runtime and branch their code accordingly in dozens of places across a project. This leads to repetitive, error-prone boilerplate that is hard to maintain and easy to get wrong.

With this library, a single import transparently handles all version differences — type systems, standard library renames, string handling, and more — so developers never need to write version checks themselves.

---

## Core Features (User Stories)

### Feature 1: Version Detection

**As a developer**, I want to know which Python version is currently running, so I can make version-aware decisions without writing version checks manually.

**Expected Usage:**

When the program runs, it should detect the current Python major version and print a human-readable label identifying whether it is running under Python 2 or Python 3.

**Test Cases:** `tests/test_cases/feature1_version_detection.json`

```json
{
    "description": "No input required. The program detects the running Python version and prints the corresponding label.",
    "cases": [
        {
            "input": "",
            "expected_output": ["Python 2", "Python 3"]
        }
    ]
}
```

---

### Feature 2: Type Checking

**As a developer**, I want to check whether a value is a string or an integer without worrying about how these types differ between Python 2 and Python 3.

**Expected Usage:**

Given an arbitrary input value, the program should correctly classify it as `"string"`, `"integer"`, or `"other"`, regardless of which Python version is running.

**Test Cases:** `tests/test_cases/feature2_type_checking.json`

```json
{
    "description": "Given a value as input, print its type classification: string, integer, or other.",
    "cases": [
        {"input": "hello",  "expected_output": "string"},
        {"input": "42",     "expected_output": "integer"},
        {"input": "3.14",   "expected_output": "other"}
    ]
}
```

---

### Feature 3: Standard Library Compatibility

**As a developer**, I want to use standard library modules such as URL parsing, queue, and config file reading without worrying about the fact that they were renamed or reorganized between Python 2 and Python 3.

**Expected Usage:**

*3.1 URL Parsing — Extract scheme*

Given a URL string, the program should output the protocol scheme (e.g. `https`, `ftp`).

**Test Cases:** `tests/test_cases/feature3_1_urlparse.json`

```json
{
    "description": "Given a URL string, print its protocol scheme.",
    "cases": [
        {"input": "https://example.com/path?query=1", "expected_output": "https"},
        {"input": "ftp://files/doc.xml",              "expected_output": "ftp"}
    ]
}
```

*3.2 Queue — Enqueue then Dequeue*

Given a string, the program should put it into a queue and immediately retrieve and print it.

**Test Cases:** `tests/test_cases/feature3_2_queue.json`

```json
{
    "description": "Given a string, push it onto a queue then pop and print it.",
    "cases": [
        {"input": "hello", "expected_output": "hello"},
        {"input": "world", "expected_output": "world"}
    ]
}
```

*3.3 Config Parser — Read a config value*

Given a section name and key separated by a space, the program should look up the value from a built-in in-memory config and print it.

**Test Cases:** `tests/test_cases/feature3_3_configparser.json`

```json
{
    "description": "Given a section and key separated by a space, look up and print the value from a built-in in-memory config. The config contains: [server] host=localhost, port=8080.",
    "cases": [
        {"input": "server host", "expected_output": "localhost"},
        {"input": "server port", "expected_output": "8080"}
    ]
}
```

---

### Feature 4: String and Bytes Conversion

**As a developer**, I want to safely convert between text strings and byte strings without worrying about the underlying type differences between Python 2 and Python 3.

**Expected Usage:**

*4.1 Text to Bytes*

Given a plain text string, the program should convert it to its bytes representation and print it.

**Test Cases:** `tests/test_cases/feature4_1_ensure_binary.json`

```json
{
    "description": "Given a plain text string, convert it to bytes and print the bytes representation.",
    "cases": [
        {"input": "hello", "expected_output": "b'hello'"},
        {"input": "world", "expected_output": "b'world'"}
    ]
}
```

*4.2 Bytes to Text*

Given a byte string literal (e.g. `b'hello'`), the program should decode it to a text string and print it.

**Test Cases:** `tests/test_cases/feature4_2_ensure_text.json`

```json
{
    "description": "Given a bytes literal as a string (e.g. b'hello'), decode it and print the resulting text.",
    "cases": [
        {"input": "b'hello'", "expected_output": "hello"},
        {"input": "b'world'", "expected_output": "world"}
    ]
}
```

---

### Feature 5: Dictionary Iteration

**As a developer**, I want to iterate over dictionary keys, values, and key-value pairs in a memory-efficient way that works identically on both Python versions.

**Expected Usage:**

Given a dictionary described as a comma-separated list of `key:value` pairs, followed by a mode flag (`keys`, `values`, or `items`), the program should print the corresponding output sorted and formatted as described below.

*5.1 Iterate Keys*

**Test Cases:** `tests/test_cases/feature5_1_iterkeys.json`

```json
{
    "description": "Given a dictionary as comma-separated key:value pairs, print all keys sorted alphabetically, one per line.",
    "cases": [
        {"input": "a:1,b:2,c:3", "expected_output": "a\nb\nc"}
    ]
}
```

*5.2 Iterate Values*

**Test Cases:** `tests/test_cases/feature5_2_itervalues.json`

```json
{
    "description": "Given a dictionary as comma-separated key:value pairs, print all values sorted by their key alphabetically, one per line.",
    "cases": [
        {"input": "a:1,b:2,c:3", "expected_output": "1\n2\n3"}
    ]
}
```

*5.3 Iterate Items*

**Test Cases:** `tests/test_cases/feature5_3_iteritems.json`

```json
{
    "description": "Given a dictionary as comma-separated key:value pairs, print all key-value pairs sorted by key, formatted as key=value, one per line.",
    "cases": [
        {"input": "a:1,b:2,c:3", "expected_output": "a=1\nb=2\nc=3"}
    ]
}
```

---

### Feature 6: Metaclass Compatibility

**As a developer**, I want to define classes with custom metaclasses using syntax that works on both Python 2 and Python 3, since the two versions use incompatible syntax for this.

**Expected Usage:**

Given a class name as input, the program should create that class using a custom metaclass that automatically injects an `injected = True` attribute, then print whether the attribute exists and the metaclass was correctly applied.

**Test Cases:** `tests/test_cases/feature6_metaclass.json`

```json
{
    "description": "Given a class name, dynamically create it using a custom metaclass that injects injected=True, then print whether the injection succeeded.",
    "cases": [
        {"input": "MyClass",      "expected_output": "True"},
        {"input": "AnotherClass", "expected_output": "True"}
    ]
}
```

---

### Feature 7: Print Function

**As a developer**, I want to use print as a regular function with keyword arguments such as custom separators, in a way that is valid syntax on both Python 2 and Python 3.

**Expected Usage:**

Given a line of space-separated words, the program should print them joined by a single space.

**Test Cases:** `tests/test_cases/feature7_print.json`

```json
{
    "description": "Given space-separated words as input, print them joined by a single space.",
    "cases": [
        {"input": "Hello World",  "expected_output": "Hello World"},
        {"input": "foo bar baz",  "expected_output": "foo bar baz"}
    ]
}
```

---

### Feature 8: Exception Re-raising

**As a developer**, I want to catch an exception, wrap it in a new exception type, and re-raise it while preserving the original traceback, using syntax that is valid on both Python versions.

**Expected Usage:**

Given an original error message, the program should raise it as a base exception, catch it, wrap the message into a new exception, and print the type and message of the final raised exception.

**Test Cases:** `tests/test_cases/feature8_reraise.json`

```json
{
    "description": "Given an original error message, raise it, catch it, wrap it into a RuntimeError, and print the type and final message.",
    "cases": [
        {"input": "original error", "expected_output": "RuntimeError: wrapped: original error"},
        {"input": "bad input",      "expected_output": "RuntimeError: wrapped: bad input"}
    ]
}
```

---

### Feature 9: In-memory String and Bytes Buffers

**As a developer**, I want in-memory buffer objects for both text and binary data that work consistently across Python versions.

**Expected Usage:**

*9.1 Text Buffer*

Given a text string, the program should write it to an in-memory text buffer, read it back, and print it.

**Test Cases:** `tests/test_cases/feature9_1_stringio.json`

```json
{
    "description": "Given a text string, write it to an in-memory text buffer, read it back, and print it.",
    "cases": [
        {"input": "hello world", "expected_output": "hello world"},
        {"input": "goodbye",     "expected_output": "goodbye"}
    ]
}
```

*9.2 Binary Buffer*

Given a plain ASCII string, the program should encode it to bytes, write to a binary buffer, read it back, decode, and print.

**Test Cases:** `tests/test_cases/feature9_2_bytesio.json`

```json
{
    "description": "Given a plain ASCII string, encode to bytes, write to a binary buffer, read back, decode, and print.",
    "cases": [
        {"input": "hello", "expected_output": "hello"},
        {"input": "data",  "expected_output": "data"}
    ]
}
```

---

### Feature 10: Iterator Advancement

**As a developer**, I want a single, consistent way to advance an iterator by one step and retrieve its next value, regardless of which Python version is running.

**Expected Usage:**

Given a comma-separated list of integers and a count `n` separated by a space, the program should advance the iterator `n` times and print each retrieved value on a separate line. If the iterator is exhausted before `n` steps, print `StopIteration`.

**Test Cases:** `tests/test_cases/feature10_next.json`

```json
{
    "description": "Given a comma-separated integer list and a count n separated by a space, print the first n values from the iterator one per line. Print StopIteration if the iterator runs out.",
    "cases": [
        {"input": "1,2,3 2", "expected_output": "1\n2"},
        {"input": "4,5 3",   "expected_output": "4\n5\nStopIteration"}
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_[name].json` should write its output to `tests/stdout/feature1_[name]@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.

