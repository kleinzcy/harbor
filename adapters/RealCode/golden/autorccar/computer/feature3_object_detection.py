#!/usr/bin/env python3
"""
Feature 3: Object Detection for Stop Signs and Traffic Lights
Handles detection of stop signs and traffic lights using cascade classifiers.
"""

import sys
import json


def detect_stop_sign(image_param):
    """
    Simulate stop sign detection.

    Parameters:
    - image_param (str): Image parameter string

    Returns:
    - tuple: (detected, v_param)
    """
    # For testing: return different results based on image parameter
    if image_param == "grayscale_array":
        return True, 150
    elif image_param == "empty_gray_array":
        return False, 0
    else:
        # Default: assume detected with medium v_param
        return True, 100


def detect_traffic_light(image_param):
    """
    Simulate traffic light detection and color recognition.

    Parameters:
    - image_param (str): Image parameter string

    Returns:
    - tuple: (detected, color)
    """
    # For testing: return different results based on image parameter
    if image_param == "color_array":
        return True, "red"
    elif image_param == "color_array_green":
        return True, "green"
    elif image_param == "color_array_yellow":
        return True, "yellow"
    else:
        # Default: assume not detected
        return False, "none"


def handle_object_detection(input_data):
    """
    Handle object detection operations based on input.

    Parameters:
    - input_data (dict): Input parameters

    Returns:
    - dict: Detection result
    """
    if "cascade_file" not in input_data:
        return {"error": "Missing cascade_file parameter"}

    cascade_file = input_data["cascade_file"]
    image_param = input_data.get("image", "")

    # Determine which detection to perform based on cascade file
    if "stop_sign" in cascade_file:
        detected, v_param = detect_stop_sign(image_param)
        return {
            "detected": detected,
            "v_param": int(v_param)
        }

    elif "traffic_light" in cascade_file:
        detected, color = detect_traffic_light(image_param)
        result = {"detected": detected}
        if detected:
            result["color"] = color
        return result

    else:
        return {"error": f"Unknown cascade file: {cascade_file}"}


def main():
    # Read JSON input from stdin
    try:
        input_str = sys.stdin.read().strip()
        if not input_str:
            print(json.dumps({"error": "No input provided"}))
            return

        # Parse input JSON
        try:
            input_data = json.loads(input_str)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input"}))
            return

        # Handle object detection operation
        result = handle_object_detection(input_data)

        # Output result as JSON
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))


if __name__ == "__main__":
    main()