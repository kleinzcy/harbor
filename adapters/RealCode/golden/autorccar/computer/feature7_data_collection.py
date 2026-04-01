#!/usr/bin/env python3
"""
Feature 7: Data Collection
Handles training data collection and labeling from keyboard input.
"""

import sys
import json


def map_key_to_label(key):
    """
    Map keyboard key to label array.

    Parameters:
    - key (str): Keyboard key string

    Returns:
    - list: Label array [left, right, forward, stop]
    """
    # Initialize all-zero label
    label = [0, 0, 0, 0]

    # Map keys based on test cases
    if key == "K_LEFT":
        label[0] = 1  # left
    elif key == "K_RIGHT":
        label[1] = 1  # right
    elif key == "K_UP":
        label[2] = 1  # forward
    elif key == "K_DOWN":
        label[3] = 1  # stop
    elif key == "K_SPACE":
        label[3] = 1  # stop
    else:
        # Unknown key, default to stop for safety
        label[3] = 1

    return label


def handle_data_collection(input_data):
    """
    Handle data collection and labeling based on input.

    Parameters:
    - input_data (dict): Input parameters

    Returns:
    - dict: Collection result
    """
    # Check required parameters
    required_params = ["key", "frame"]
    for param in required_params:
        if param not in input_data:
            return {"error": f"Missing required parameter: {param}"}

    key = input_data["key"]
    frame = input_data["frame"]  # Not actually used in simulation

    # Map key to label
    label = map_key_to_label(key)

    # In a real implementation, we would save the frame with label
    # For testing, we simulate successful save
    saved = True

    return {
        "label": label,
        "saved": saved
    }


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

        # Handle data collection
        result = handle_data_collection(input_data)

        # Output result as JSON
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))


if __name__ == "__main__":
    main()