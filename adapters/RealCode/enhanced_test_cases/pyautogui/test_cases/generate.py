#!/usr/bin/env python3
import json
import os

def enhance_feature1(existing):
    """Add new test cases to feature1_mouse.json"""
    new_cases = []
    # 1. moveTo edge of screen
    new_cases.append({
        "input": {
            "test_type": "mouse_move",
            "operation": "moveTo",
            "x": 0,
            "y": 0,
            "duration": 0,
            "tween": "linear"
        },
        "expected_output": {
            "success": True,
            "position_within_tolerance": True
        }
    })
    new_cases.append({
        "input": {
            "test_type": "mouse_move",
            "operation": "moveTo",
            "x": 1919,
            "y": 1079,
            "duration": 0,
            "tween": "linear"
        },
        "expected_output": {
            "success": True,
            "position_within_tolerance": True
        }
    })
    # 2. moveTo negative coordinates
    new_cases.append({
        "input": {
            "test_type": "mouse_move",
            "operation": "moveTo",
            "x": -100,
            "y": -200,
            "duration": 0,
            "tween": "linear"
        },
        "expected_output": {
            "success": True,
            "position_within_tolerance": True
        }
    })
    # 3. moveTo with easeInOut tween
    new_cases.append({
        "input": {
            "test_type": "mouse_move",
            "operation": "moveTo",
            "x": 500,
            "y": 500,
            "duration": 0.5,
            "tween": "easeInOut"
        },
        "expected_output": {
            "success": True,
            "position_within_tolerance": True
        }
    })
    # 4. moveRel large offset
    new_cases.append({
        "input": {
            "test_type": "mouse_move",
            "operation": "moveRel",
            "xOffset": 5000,
            "yOffset": 5000,
            "duration": 0
        },
        "expected_output": {
            "success": True,
            "position_within_tolerance": True
        }
    })
    # 5. tripleClick middle button
    new_cases.append({
        "input": {
            "test_type": "mouse_click",
            "operation": "tripleClick",
            "x": 300,
            "y": 300,
            "button": "middle"
        },
        "expected_output": {
            "success": True,
            "click_count_valid": True,
            "button": "middle"
        }
    })
    # 6. mouseDown and mouseUp (separate test types not defined; need to add test_type mouse_down and mouse_up? Not in handler. We'll skip for now.
    # 7. dragTo absolute
    new_cases.append({
        "input": {
            "test_type": "mouse_drag",
            "operation": "dragTo",
            "x": 400,
            "y": 400,
            "duration": 0.5,
            "button": "left"
        },
        "expected_output": {
            "success": True,
            "drag_completed": True
        }
    })
    # 8. hscroll and vscroll (test_type mouse_scroll with operation hscroll/vscroll)
    new_cases.append({
        "input": {
            "test_type": "mouse_scroll",
            "operation": "hscroll",
            "clicks": 3
        },
        "expected_output": {
            "success": True,
            "scroll_detected": True
        }
    })
    new_cases.append({
        "input": {
            "test_type": "mouse_scroll",
            "operation": "vscroll",
            "clicks": -2
        },
        "expected_output": {
            "success": True,
            "scroll_detected": True
        }
    })
    # 9. scroll negative clicks
    new_cases.append({
        "input": {
            "test_type": "mouse_scroll",
            "operation": "scroll",
            "clicks": -10
        },
        "expected_output": {
            "success": True,
            "scroll_detected": True
        }
    })
    # 10. failsafe trigger (requires FAILSAFE enabled). Need to enable failsafe first? We'll assume default is True.
    # Move to failsafe point (0,0) should raise FailSafeException, but test runner expects success? Let's see handler: run_mouse_move_test catches Exception and returns success False.
    # We'll add a test case that expects success False and error contains 'FailSafeException'.
    # However, we need to ensure FAILSAFE is True. We'll add a separate test for failsafe config.
    # For now, skip.

    # Append new cases to existing cases
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature2(existing):
    new_cases = []
    # 1. typewrite empty string
    new_cases.append({
        "input": {
            "test_type": "keyboard_type",
            "text": "",
            "interval": 0.1
        },
        "expected_output": {
            "success": True,
            "text_typed": True,
            "timing_within_tolerance": True
        }
    })
    # 2. typewrite with interval 0
    new_cases.append({
        "input": {
            "test_type": "keyboard_type",
            "text": "test",
            "interval": 0
        },
        "expected_output": {
            "success": True,
            "text_typed": True,
            "timing_within_tolerance": True
        }
    })
    # 3. typewrite with special characters
    new_cases.append({
        "input": {
            "test_type": "keyboard_type",
            "text": "!@#$%^&*()",
            "interval": 0.05
        },
        "expected_output": {
            "success": True,
            "text_typed": True,
            "timing_within_tolerance": True
        }
    })
    # 4. press with invalid key (should still succeed? mock's isValidKey returns True for printable char)
    new_cases.append({
        "input": {
            "test_type": "keyboard_press",
            "keys": "invalidkey",
            "presses": 1
        },
        "expected_output": {
            "success": True,
            "press_count": 1,
            "keys_pressed": 1
        }
    })
    # 5. press with empty list (edge case)
    new_cases.append({
        "input": {
            "test_type": "keyboard_press",
            "keys": [],
            "presses": 1
        },
        "expected_output": {
            "success": True,
            "press_count": 1,
            "keys_pressed": 0
        }
    })
    # 6. hotkey with three keys
    new_cases.append({
        "input": {
            "test_type": "keyboard_hotkey",
            "keys": ["ctrl", "shift", "c"]
        },
        "expected_output": {
            "success": True,
            "combination_recognized": True
        }
    })
    # 7. isShiftCharacter with non-character
    new_cases.append({
        "input": {
            "test_type": "keyboard_validation",
            "character": "ab"
        },
        "expected_output": {
            "is_shift_character": False
        }
    })
    # 8. isValidKey with empty string
    new_cases.append({
        "input": {
            "test_type": "keyboard_validation",
            "key": ""
        },
        "expected_output": {
            "is_valid_key": False
        }
    })
    # 9. keyDown/keyUp not in test_type mapping; skip.

    existing["cases"].extend(new_cases)
    return existing

def enhance_feature3(existing):
    new_cases = []
    # 1. screenshot without filename
    new_cases.append({
        "input": {
            "test_type": "screenshot",
            "region": [10, 10, 100, 100]
        },
        "expected_output": {
            "success": True,
            "image_captured": True,
            "file_exists": False
        }
    })
    # 2. screenshot region outside screen
    new_cases.append({
        "input": {
            "test_type": "screenshot",
            "region": [-10, -10, 50, 50],
            "save_filename": "test_outside.png"
        },
        "expected_output": {
            "success": True,
            "image_captured": True,
            "file_exists": True
        }
    })
    # 3. pixel color out of bounds (mock returns white)
    new_cases.append({
        "input": {
            "test_type": "pixel_color",
            "x": -5,
            "y": -5
        },
        "expected_output": {
            "success": True,
            "color_format_valid": True,
            "color": [255, 255, 255]
        }
    })
    # 4. pixel match with tolerance large
    new_cases.append({
        "input": {
            "test_type": "pixel_match",
            "x": 100,
            "y": 100,
            "expected_rgb": [0, 0, 0],
            "tolerance": 255
        },
        "expected_output": {
            "success": True,
            "match_result": False  # mock always returns False
        }
    })
    # 5. image locate with confidence 0.0 (should still not find)
    new_cases.append({
        "input": {
            "test_type": "image_locate",
            "image_path": "nonexistent.png",
            "confidence": 0.0,
            "region": [0, 0, 100, 100]
        },
        "expected_output": {
            "success": True,
            "location_found": False
        }
    })
    # 6. image locate with grayscale parameter (not in input schema; skip)
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature4(existing):
    new_cases = []
    # 1. alert empty text and title
    new_cases.append({
        "input": {
            "test_type": "alert",
            "text": "",
            "title": ""
        },
        "expected_output": {
            "return_value": "OK"
        }
    })
    # 2. confirm with one button
    new_cases.append({
        "input": {
            "test_type": "confirm",
            "text": "Only OK",
            "buttons": ["OK"]
        },
        "expected_output": {
            "return_value_in": ["OK"],
            "return_value": "OK"
        }
    })
    # 3. confirm with three buttons
    new_cases.append({
        "input": {
            "test_type": "confirm",
            "text": "Choose",
            "buttons": ["Yes", "No", "Cancel"]
        },
        "expected_output": {
            "return_value_in": ["Yes", "No", "Cancel"],
            "return_value": "Yes"
        }
    })
    # 4. prompt with empty default
    new_cases.append({
        "input": {
            "test_type": "prompt",
            "text": "Name?",
            "default": ""
        },
        "expected_output": {
            "return_value_type": "str",
            "return_value": ""
        }
    })
    # 5. password with empty mask
    new_cases.append({
        "input": {
            "test_type": "password",
            "text": "Password:",
            "mask": ""
        },
        "expected_output": {
            "return_value_type": "str",
            "return_value": ""
        }
    })
    # 6. password with default value
    new_cases.append({
        "input": {
            "test_type": "password",
            "text": "Password:",
            "default": "secret",
            "mask": "*"
        },
        "expected_output": {
            "return_value_type": "str",
            "return_value": "secret"
        }
    })
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature5(existing):
    new_cases = []
    # 1. coordinate check with floating point
    new_cases.append({
        "input": {
            "test_type": "coordinate_check",
            "x": 123.456,
            "y": 789.012
        },
        "expected_output": {
            "on_screen": True
        }
    })
    # 2. coordinate check with extreme negative
    new_cases.append({
        "input": {
            "test_type": "coordinate_check",
            "x": -1000,
            "y": -1000
        },
        "expected_output": {
            "on_screen": False
        }
    })
    # 3. geometric calculation with n=0
    new_cases.append({
        "input": {
            "test_type": "geometric_calculation",
            "x1": 0,
            "y1": 0,
            "x2": 100,
            "y2": 100,
            "n": 0
        },
        "expected_output": {
            "point": [0, 0]
        }
    })
    # 4. geometric calculation with n=1
    new_cases.append({
        "input": {
            "test_type": "geometric_calculation",
            "x1": 0,
            "y1": 0,
            "x2": 100,
            "y2": 100,
            "n": 1
        },
        "expected_output": {
            "point": [100, 100]
        }
    })
    # 5. geometric calculation with n outside range (should extrapolate)
    new_cases.append({
        "input": {
            "test_type": "geometric_calculation",
            "x1": 0,
            "y1": 0,
            "x2": 100,
            "y2": 100,
            "n": 2
        },
        "expected_output": {
            "point": [200, 200]
        }
    })
    # 6. mouse_position after moving mouse (not needed)
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature6(existing):
    new_cases = []
    # 1. failsafe config disable
    new_cases.append({
        "input": {
            "test_type": "failsafe_config",
            "enable": False
        },
        "expected_output": {
            "failsafe_enabled": False
        }
    })
    # 2. pause config zero
    new_cases.append({
        "input": {
            "test_type": "pause_config",
            "seconds": 0
        },
        "expected_output": {
            "pause_set": 0
        }
    })
    # 3. pause config negative (should still set?)
    new_cases.append({
        "input": {
            "test_type": "pause_config",
            "seconds": -1
        },
        "expected_output": {
            "pause_set": -1
        }
    })
    # 4. exception trigger for FailSafeException (need to trigger by moving to failsafe point)
    # Not directly supported; we can add a test that moves mouse to failsafe point with failsafe enabled and expect exception_raised true.
    # But test_type exception_trigger only handles ImageNotFoundException.
    # We'll skip.
    # 5. failsafe_points after configuration change? Not needed.
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature7(existing):
    new_cases = []
    # 1. dependency check for nonexistent module
    new_cases.append({
        "input": {
            "test_type": "dependency_check",
            "module": "nonexistent_module"
        },
        "expected_output": {
            "available": False
        }
    })
    # 2. platform functionality for click
    new_cases.append({
        "input": {
            "test_type": "platform_functionality",
            "function": "click",
            "x": 100,
            "y": 100
        },
        "expected_output": {
            "success": True
        }
    })
    # 3. platform functionality for typewrite
    new_cases.append({
        "input": {
            "test_type": "platform_functionality",
            "function": "typewrite",
            "text": "hello"
        },
        "expected_output": {
            "success": True
        }
    })
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature8(existing):
    new_cases = []
    # 1. timing validation with zero interval
    new_cases.append({
        "input": {
            "test_type": "timing_validation",
            "operation": "typewrite",
            "text": "Hello",
            "interval": 0
        },
        "expected_output": {
            "duration_within_tolerance": True
        }
    })
    # 2. timing validation with long interval
    new_cases.append({
        "input": {
            "test_type": "timing_validation",
            "operation": "typewrite",
            "text": "Hi",
            "interval": 1.0
        },
        "expected_output": {
            "duration_within_tolerance": True
        }
    })
    # 3. multithreading with zero threads (edge)
    new_cases.append({
        "input": {
            "test_type": "multithreading",
            "threads": 0,
            "operations": []
        },
        "expected_output": {
            "all_threads_completed": True,
            "no_deadlocks": True
        }
    })
    # 4. memory usage with zero iterations
    new_cases.append({
        "input": {
            "test_type": "memory_usage",
            "iterations": 0,
            "operation": "click"
        },
        "expected_output": {
            "memory_increase_below_threshold": True
        }
    })
    # 5. long running with zero duration
    new_cases.append({
        "input": {
            "test_type": "long_running",
            "duration_seconds": 0,
            "operations_per_second": 10
        },
        "expected_output": {
            "success": True,
            "no_crashes": True
        }
    })
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature9(existing):
    new_cases = []
    # 1. parameter normalization with tuple input
    new_cases.append({
        "input": {
            "test_type": "parameter_normalization",
            "x": (100,),
            "y": (200,)
        },
        "expected_output": {
            "normalized": True,
            "x": 100.0,
            "y": 200.0
        }
    })
    # 2. parameter normalization with None (should raise error)
    new_cases.append({
        "input": {
            "test_type": "parameter_normalization",
            "x": None,
            "y": None
        },
        "expected_output": {
            "normalized": False,
            "error": ".*"
        }
    })
    # 3. boundary check with extreme positive coordinates
    new_cases.append({
        "input": {
            "test_type": "boundary_check",
            "x": 10000,
            "y": 10000
        },
        "expected_output": {
            "handled_gracefully": True
        }
    })
    # 4. error handling for _getQuotedStringToken
    new_cases.append({
        "input": {
            "test_type": "error_handling",
            "operation": "_getQuotedStringToken",
            "input": "hello"
        },
        "expected_output": {
            "exception_raised": True
        }
    })
    # 5. coordinate wrapping with negative large
    new_cases.append({
        "input": {
            "test_type": "coordinate_wrapping",
            "x": -10000,
            "y": -10000
        },
        "expected_output": {
            "within_bounds": False
        }
    })
    existing["cases"].extend(new_cases)
    return existing

def enhance_feature10(existing):
    new_cases = []
    # 1. api availability for all common functions
    new_cases.append({
        "input": {
            "test_type": "api_availability",
            "function_names": ["moveTo", "moveRel", "click", "rightClick", "doubleClick", "tripleClick", "mouseDown", "mouseUp", "dragTo", "dragRel", "scroll", "hscroll", "vscroll", "typewrite", "press", "keyDown", "keyUp", "hold", "hotkey", "isShiftCharacter", "isValidKey", "screenshot", "locateOnScreen", "locateAllOnScreen", "locateCenterOnScreen", "pixel", "pixelMatchesColor", "locate", "locateAll", "center", "alert", "confirm", "prompt", "password", "size", "position", "onScreen", "getPointOnLine", "set_failsafe", "set_pause", "get_failsafe_points", "platform", "check_dependency", "_normalizeXYArgs", "_getNumberToken", "_getQuotedStringToken"]
        },
        "expected_output": {
            "all_functions_available": True
        }
    })
    # 2. constant validation for all known constants
    new_cases.append({
        "input": {
            "test_type": "constant_validation",
            "constants": ["FAILSAFE", "PAUSE", "MINIMUM_DURATION", "PRIMARY", "SECONDARY", "LEFT", "RIGHT", "MIDDLE"]
        },
        "expected_output": {
            "all_constants_defined": True
        }
    })
    # 3. example code for other examples (just placeholder)
    new_cases.append({
        "input": {
            "test_type": "example_code",
            "example": "keyboard_shortcuts"
        },
        "expected_output": {
            "success": True
        }
    })
    existing["cases"].extend(new_cases)
    return existing

def main():
    base_dir = "test_cases"
    out_dir = "enhanced_test_cases"
    os.makedirs(out_dir, exist_ok=True)

    features = [
        ("feature1_mouse.json", enhance_feature1),
        ("feature2_keyboard.json", enhance_feature2),
        ("feature3_screen.json", enhance_feature3),
        ("feature4_msgbox.json", enhance_feature4),
        ("feature5_screeninfo.json", enhance_feature5),
        ("feature6_safety.json", enhance_feature6),
        ("feature7_platform.json", enhance_feature7),
        ("feature8_performance.json", enhance_feature8),
        ("feature9_validation.json", enhance_feature9),
        ("feature10_documentation.json", enhance_feature10),
    ]

    for filename, enhancer in features:
        path = os.path.join(base_dir, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        enhanced = enhancer(data)
        out_path = os.path.join(out_dir, filename)
        with open(out_path, 'w') as f:
            json.dump(enhanced, f, indent=2)
        print(f"Enhanced {filename}: {len(enhanced['cases'])} total cases")

if __name__ == "__main__":
    main()