# PyAutoGUI Test Suite - Automated Testing Framework for PyAutoGUI

## Project Goal

Build a comprehensive automated testing framework for PyAutoGUI that validates all core functionality across mouse operations, keyboard input, screen capture, image recognition, message boxes, and safety mechanisms without requiring manual intervention or platform-specific test scripts.

---

## Background & Problem

Without this test suite, developers must manually test PyAutoGUI functionality across different platforms (Windows, macOS, Linux), leading to inconsistent test coverage, difficulty reproducing issues, and time-consuming regression testing. This results in undetected bugs, platform-specific failures, and maintenance challenges as the library evolves.

With this test suite, developers can run automated tests that consistently validate PyAutoGUI functionality across all supported platforms, ensuring reliability, catching regressions early, and providing clear test reports for each feature.

---

## Core Features

### Feature 1: Mouse Operation Testing

**As a developer**, I want to automatically test all mouse-related functions (movement, clicking, dragging, scrolling) with various parameters (absolute/relative coordinates, animation effects, click types), so I can verify coordinate accuracy, boundary conditions, and animation smoothness.

**Expected Behavior / Usage:**

The test suite should simulate mouse operations in a controlled environment, validating that movements reach correct coordinates, clicks register properly, drag operations work correctly, and scroll functions behave as expected. Tests should cover edge cases like off-screen coordinates and different button configurations.

*1.1 Movement Testing — Validate absolute and relative movement*

- Test `moveTo()` with various coordinates and duration parameters
- Test `moveRel()` with positive and negative offsets
- Verify tweening functions produce smooth animations
- Validate coordinate boundary handling

*1.2 Click Testing — Validate click operations*

- Test `click()`, `doubleClick()`, `rightClick()`, `tripleClick()`
- Verify click counts, intervals, and button parameters
- Test `mouseDown()` and `mouseUp()` state management

*1.3 Drag Testing — Validate drag operations*

- Test `dragTo()` and `dragRel()` with various distances and durations
- Verify button parameter functionality

*1.4 Scroll Testing — Validate scroll operations*

- Test `scroll()`, `hscroll()`, `vscroll()` with positive/negative clicks
- Verify scroll position parameters

**Test Cases:** `tests/test_cases/feature1_mouse.json`

```json
{
    "description": "Comprehensive mouse operation validation with coordinate boundaries and animation parameters",
    "cases": [
        {
            "input": {"test_type": "mouse_move", "operation": "moveTo", "x": 100, "y": 200, "duration": 0.5, "tween": "linear"},
            "expected_output": {"success": true, "position_within_tolerance": true}
        },
        {
            "input": {"test_type": "mouse_move", "operation": "moveRel", "xOffset": 50, "yOffset": -30, "duration": 0},
            "expected_output": {"success": true, "position_within_tolerance": true}
        },
        {
            "input": {"test_type": "mouse_click", "operation": "click", "x": 150, "y": 250, "clicks": 2, "button": "left"},
            "expected_output": {"success": true, "click_count_valid": true}
        },
        {
            "input": {"test_type": "mouse_click", "operation": "rightClick", "x": 300, "y": 400},
            "expected_output": {"success": true, "button": "right"}
        },
        {
            "input": {"test_type": "mouse_drag", "operation": "dragRel", "xOffset": 100, "yOffset": 100, "duration": 1.0, "button": "left"},
            "expected_output": {"success": true, "drag_completed": true}
        },
        {
            "input": {"test_type": "mouse_scroll", "operation": "scroll", "clicks": 5},
            "expected_output": {"success": true, "scroll_detected": true}
        }
    ]
}
```

---

### Feature 2: Keyboard Operation Testing

**As a developer**, I want to automatically test keyboard input, key simulation, combination keys, and hotkeys, so I can ensure proper character encoding, key mapping, and input speed control.

**Expected Behavior / Usage:**

The test suite should simulate keyboard input and verify that text is typed correctly, special keys function properly, modifier key combinations work, and input intervals are respected. Tests should include edge cases like invalid keys and shift character detection.

*2.1 Text Input Testing — Validate typing functionality*

- Test `typewrite()` with strings, lists, and intervals
- Verify special characters and newline handling

*2.2 Key Press Testing — Validate key press operations*

- Test `press()` with single keys and key lists
- Verify `keyDown()` and `keyUp()` state management
- Test `hold()` functionality

*2.3 Hotkey Testing — Validate key combinations*

- Test `hotkey()` with common combinations (Ctrl+C, Ctrl+V)
- Verify modifier key sequencing

*2.4 Validation Testing — Validate key and character checks*

- Test `isShiftCharacter()` with various characters
- Test `isValidKey()` with valid and invalid keys

**Test Cases:** `tests/test_cases/feature2_keyboard.json`

```json
{
    "description": "Keyboard input simulation with various key types, combinations, and timing parameters",
    "cases": [
        {
            "input": {"test_type": "keyboard_type", "text": "Hello World!", "interval": 0.1},
            "expected_output": {"success": true, "text_typed": true, "timing_within_tolerance": true}
        },
        {
            "input": {"test_type": "keyboard_press", "keys": "enter", "presses": 2, "interval": 0.05},
            "expected_output": {"success": true, "press_count": 2}
        },
        {
            "input": {"test_type": "keyboard_press", "keys": ["a", "b", "c"], "presses": 1},
            "expected_output": {"success": true, "keys_pressed": 3}
        },
        {
            "input": {"test_type": "keyboard_hotkey", "keys": ["ctrl", "c"]},
            "expected_output": {"success": true, "combination_recognized": true}
        },
        {
            "input": {"test_type": "keyboard_validation", "character": "A"},
            "expected_output": {"is_shift_character": true}
        },
        {
            "input": {"test_type": "keyboard_validation", "character": "a"},
            "expected_output": {"is_shift_character": false}
        },
        {
            "input": {"test_type": "keyboard_validation", "key": "f12"},
            "expected_output": {"is_valid_key": true}
        }
    ]
}
```

---

### Feature 3: Screen Capture & Image Recognition Testing

**As a developer**, I want to automatically test screen capture, image searching, and image matching functions, so I can verify the accuracy and performance of image processing operations.

**Expected Behavior / Usage:**

The test suite should capture screen regions, save images in various formats, search for images within screens or other images, and validate pixel color matching. Tests should include confidence-based matching, multi-monitor support, and performance measurements.

*3.1 Screenshot Testing — Validate screen capture functionality*

- Test `screenshot()` with full screen and region parameters
- Verify image format support and saving functionality

*3.2 Image Location Testing — Validate image finding on screen*

- Test `locateOnScreen()`, `locateAllOnScreen()`, `locateCenterOnScreen()`
- Verify confidence parameter, grayscale mode, and region limiting

*3.3 Pixel Operation Testing — Validate pixel color functions*

- Test `pixel()` color retrieval
- Test `pixelMatchesColor()` with tolerance parameters

*3.4 Image Search Testing — Validate image within image finding*

- Test `locate()` and `locateAll()` with known test images
- Verify `center()` region calculation

**Test Cases:** `tests/test_cases/feature3_screen.json`

```json
{
    "description": "Screen capture and image recognition with region, confidence, and color matching parameters",
    "cases": [
        {
            "input": {"test_type": "screenshot", "region": [0, 0, 100, 100], "save_filename": "test_screenshot.png"},
            "expected_output": {"success": true, "image_captured": true, "file_exists": true}
        },
        {
            "input": {"test_type": "pixel_color", "x": 50, "y": 50},
            "expected_output": {"success": true, "color_format_valid": true}
        },
        {
            "input": {"test_type": "pixel_match", "x": 100, "y": 200, "expected_rgb": [255, 0, 0], "tolerance": 10},
            "expected_output": {"success": true, "match_result": false}
        },
        {
            "input": {"test_type": "image_locate", "image_path": "test_button.png", "confidence": 0.8, "region": [0, 0, 800, 600]},
            "expected_output": {"success": true, "location_found": false}
        }
    ]
}
```

---

### Feature 4: Message Box & User Interaction Testing

**As a developer**, I want to automatically test various message box types (alert, confirm, prompt, password), so I can ensure the integrity and reliability of user interaction functions.

**Expected Behavior / Usage:**

The test suite should simulate message box interactions, validate button customization, return value processing, and exception handling. Tests should cover different button configurations and input scenarios.

*4.1 Alert Box Testing — Validate basic alert functionality*

- Test `alert()` with custom text and title
- Verify return value is 'OK'

*4.2 Confirm Box Testing — Validate confirmation dialogs*

- Test `confirm()` with custom button arrays
- Verify correct button text return

*4.3 Prompt Box Testing — Validate input dialogs*

- Test `prompt()` with default values
- Verify text input and cancellation handling

*4.4 Password Box Testing — Validate password dialogs*

- Test `password()` with mask characters
- Verify password hiding functionality

**Test Cases:** `tests/test_cases/feature4_msgbox.json`

```json
{
    "description": "Message box dialog simulation with various button configurations and input scenarios",
    "cases": [
        {
            "input": {"test_type": "alert", "text": "Hello World", "title": "Test Alert"},
            "expected_output": {"return_value": "OK"}
        },
        {
            "input": {"test_type": "confirm", "text": "Continue?", "buttons": ["Yes", "No"]},
            "expected_output": {"return_value_in": ["Yes", "No"]}
        },
        {
            "input": {"test_type": "prompt", "text": "Enter name:", "default": "User"},
            "expected_output": {"return_value_type": "string"}
        },
        {
            "input": {"test_type": "password", "text": "Enter password:", "mask": "*"},
            "expected_output": {"return_value_type": "string"}
        }
    ]
}
```

---

### Feature 5: Screen Information & Coordinate System Testing

**As a developer**, I want to automatically test screen size acquisition, coordinate conversion, multi-monitor support, and coordinate verification, so I can ensure proper operation under different resolutions and monitor configurations.

**Expected Behavior / Usage:**

The test suite should retrieve screen information, validate coordinate positions, test geometric calculations, and verify multi-monitor support. Tests should adapt to different screen resolutions and configurations.

*5.1 Screen Data Testing — Validate screen information retrieval*

- Test `size()` returns valid dimensions
- Test `position()` returns current mouse coordinates

*5.2 Coordinate Validation Testing — Validate coordinate checking*

- Test `onScreen()` with valid and invalid coordinates
- Verify boundary condition handling

*5.3 Geometric Calculation Testing — Validate point calculations*

- Test `getPointOnLine()` interpolation
- Verify `Point` class arithmetic operations

**Test Cases:** `tests/test_cases/feature5_screeninfo.json`

```json
{
    "description": "Screen information retrieval, coordinate validation, and geometric calculations",
    "cases": [
        {
            "input": {"test_type": "screen_size"},
            "expected_output": {"width_greater_than": 0, "height_greater_than": 0}
        },
        {
            "input": {"test_type": "mouse_position"},
            "expected_output": {"x_within_screen": true, "y_within_screen": true}
        },
        {
            "input": {"test_type": "coordinate_check", "x": 100, "y": 200},
            "expected_output": {"on_screen": true}
        },
        {
            "input": {"test_type": "coordinate_check", "x": -10, "y": -10},
            "expected_output": {"on_screen": false}
        },
        {
            "input": {"test_type": "geometric_calculation", "x1": 0, "y1": 0, "x2": 100, "y2": 100, "n": 0.5},
            "expected_output": {"point": [50, 50]}
        }
    ]
}
```

---

### Feature 6: Safety Functions & Exception Handling Testing

**As a developer**, I want to automatically test fail-safe mechanisms, exception capture, error recovery, and timeout processing, so I can ensure the stability and safety of automated scripts.

**Expected Behavior / Usage:**

The test suite should validate fail-safe behavior, test exception handling, verify error recovery mechanisms, and measure timeout processing. Tests should trigger safety exceptions and validate proper handling.

*6.1 Fail-Safe Testing — Validate safety mechanism*

- Test `FAILSAFE` enable/disable behavior
- Verify `FailSafeException` triggering at safe points
- Test `FAILSAFE_POINTS` configuration

*6.2 Exception Handling Testing — Validate error capture*

- Test `PyAutoGUIException` base class
- Test `ImageNotFoundException` for missing images
- Verify exception hierarchy and messaging

*6.3 Configuration Testing — Validate global settings*

- Test `PAUSE` interval control
- Test `MINIMUM_DURATION` enforcement
- Verify configuration persistence

**Test Cases:** `tests/test_cases/feature6_safety.json`

```json
{
    "description": "Safety configuration, fail-safe mechanism validation, and exception handling",
    "cases": [
        {
            "input": {"test_type": "failsafe_config", "enable": true},
            "expected_output": {"failsafe_enabled": true}
        },
        {
            "input": {"test_type": "pause_config", "seconds": 0.5},
            "expected_output": {"pause_set": 0.5}
        },
        {
            "input": {"test_type": "failsafe_points"},
            "expected_output": {"points_count": 4}
        },
        {
            "input": {"test_type": "exception_trigger", "exception_type": "ImageNotFoundException", "image_path": "nonexistent.png"},
            "expected_output": {"exception_raised": true}
        }
    ]
}
```

---

### Feature 7: Cross-Platform Compatibility Testing

**As a developer**, I want to automatically test functional consistency across different operating systems (Windows, macOS, Linux), so I can ensure the library works correctly on all supported platforms.

**Expected Behavior / Usage:**

The test suite should detect the current platform and run platform-specific tests where applicable, validating that core functionality works consistently across Windows, macOS, and Linux. Tests should handle platform-specific dependencies and API differences.

*7.1 Platform Detection Testing — Validate OS identification*

- Detect current platform (win32, darwin, linux)
- Load appropriate platform module

*7.2 Platform-Specific Function Testing — Validate OS-specific implementations*

- Test Windows Win32 API integrations
- Test macOS Cocoa API integrations
- Test Linux X11 API integrations

*7.3 Dependency Validation Testing — Validate required libraries*

- Verify `pytweening` availability for animation
- Verify `pyscreeze` availability for screen capture
- Verify `pymsgbox` availability for message boxes
- Verify `PIL` availability for image processing

**Test Cases:** `tests/test_cases/feature7_platform.json`

```json
{
    "description": "Cross-platform compatibility validation and dependency checking",
    "cases": [
        {
            "input": {"test_type": "platform_detection"},
            "expected_output": {"platform_in": ["win32", "darwin", "linux"]}
        },
        {
            "input": {"test_type": "dependency_check", "module": "pytweening"},
            "expected_output": {"available": true}
        },
        {
            "input": {"test_type": "dependency_check", "module": "pyscreeze"},
            "expected_output": {"available": true}
        },
        {
            "input": {"test_type": "platform_functionality", "function": "moveTo", "x": 100, "y": 100},
            "expected_output": {"success": true}
        }
    ]
}
```

---

### Feature 8: Performance & Stability Testing

**As a developer**, I want to automatically test long-term operation, high-frequency operations, resource utilization, and memory management, so I can ensure stability in production environments.

**Expected Behavior / Usage:**

The test suite should measure execution times, monitor resource usage, test multi-threading scenarios, and validate stability under sustained load. Tests should include timing validation, thread safety checks, and memory leak detection.

*8.1 Performance Testing — Validate operation timing*

- Measure `typewrite()` execution with intervals
- Verify `PAUSE` configuration enforcement
- Test animation duration accuracy

*8.2 Multi-Threading Testing — Validate concurrent operations*

- Test `TypewriteThread`, `PressThread`, `HoldThread` classes
- Verify thread safety for simultaneous mouse/keyboard operations
- Test resource contention handling

*8.3 Stability Testing — Validate long-term operation*

- Run sustained automation sequences
- Monitor memory usage over time
- Test recovery from error conditions

*8.4 Resource Utilization Testing — Validate system impact*

- Monitor CPU usage during operations
- Check for file descriptor leaks
- Validate clean resource release

**Test Cases:** `tests/test_cases/feature8_performance.json`

```json
{
    "description": "Performance measurement, multi-threading validation, and stability testing",
    "cases": [
        {
            "input": {"test_type": "timing_validation", "operation": "typewrite", "text": "Hello", "interval": 0.1},
            "expected_output": {"duration_within_tolerance": true}
        },
        {
            "input": {"test_type": "multithreading", "threads": 3, "operations": ["typewrite", "press", "moveTo"]},
            "expected_output": {"all_threads_completed": true, "no_deadlocks": true}
        },
        {
            "input": {"test_type": "memory_usage", "iterations": 1000, "operation": "click"},
            "expected_output": {"memory_increase_below_threshold": true}
        },
        {
            "input": {"test_type": "long_running", "duration_seconds": 30, "operations_per_second": 10},
            "expected_output": {"success": true, "no_crashes": true}
        }
    ]
}
```

---

### Feature 9: Input Verification & Error Handling Testing

**As a developer**, I want to automatically test parameter validation, boundary checking, and error handling mechanisms, so I can ensure the safety and reliability of API calls.

**Expected Behavior / Usage:**

The test suite should test invalid parameter handling, coordinate boundary validation, and exception generation for error conditions. Tests should verify proper error messages and graceful failure handling.

*9.1 Parameter Validation Testing — Validate input checking*

- Test `_normalizeXYArgs()` with various input formats
- Verify `_getNumberToken()`, `_getQuotedStringToken()` parsing
- Test invalid parameter detection

*9.2 Boundary Checking Testing — Validate coordinate limits*

- Test off-screen coordinate handling
- Verify negative coordinate behavior
- Test extreme value handling

*9.3 Error Handling Testing — Validate exception generation*

- Test `PyAutoGUIException` for invalid operations
- Verify descriptive error messages
- Test graceful degradation

**Test Cases:** `tests/test_cases/feature9_validation.json`

```json
{
    "description": "Input parameter validation, boundary checking, and error handling",
    "cases": [
        {
            "input": {"test_type": "parameter_normalization", "x": "100", "y": [200]},
            "expected_output": {"normalized": true, "x": 100, "y": 200}
        },
        {
            "input": {"test_type": "boundary_check", "x": -100, "y": -100},
            "expected_output": {"handled_gracefully": true}
        },
        {
            "input": {"test_type": "error_handling", "operation": "_getNumberToken", "input": "hello"},
            "expected_output": {"exception_raised": true}
        },
        {
            "input": {"test_type": "coordinate_wrapping", "x": 10000, "y": 10000},
            "expected_output": {"within_bounds": true}
        }
    ]
}
```

---

### Feature 10: Documentation & Example Testing

**As a developer**, I want to automatically test documentation examples and API accessibility, so I can ensure documentation accuracy and code example correctness.

**Expected Behavior / Usage:**

The test suite should run doctests, validate API accessibility, and test example code from documentation. Tests should ensure all documented functions exist and behave as described.

*10.1 Doctest Validation — Validate documentation examples*

- Run `doctest.testmod()` on pyautogui module
- Verify all doctests pass
- Test example code snippets

*10.2 API Accessibility Testing — Validate function availability*

- Verify all documented functions are importable
- Test function signatures match documentation
- Validate constant definitions

*10.3 Example Code Testing — Validate documentation examples*

- Execute code examples from README and docs
- Verify expected behavior
- Test cross-platform compatibility of examples

**Test Cases:** `tests/test_cases/feature10_documentation.json`

```json
{
    "description": "Documentation doctest validation, API accessibility checks, and example code testing",
    "cases": [
        {
            "input": {"test_type": "doctest"},
            "expected_output": {"tests_passed": true, "failures": 0}
        },
        {
            "input": {"test_type": "api_availability", "function_names": ["moveTo", "click", "typewrite", "screenshot"]},
            "expected_output": {"all_functions_available": true}
        },
        {
            "input": {"test_type": "example_code", "example": "basic_mouse_movement"},
            "expected_output": {"success": true}
        },
        {
            "input": {"test_type": "constant_validation", "constants": ["FAILSAFE", "PAUSE", "PRIMARY"]},
            "expected_output": {"all_constants_defined": true}
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable test script** that reads test case input from stdin and prints test results to stdout, matching the format described in the test cases above.

2. **Automated test suite** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_mouse.json` should write its output to `tests/stdout/feature1_mouse@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.