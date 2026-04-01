#!/usr/bin/env python3
"""
Feature 5: Sensor Fusion
Integrates ultrasonic sensor data with threshold checking for decision making.
"""

import sys
import json


def handle_sensor_fusion(input_data):
    """
    Handle sensor fusion decision making based on input.

    Parameters:
    - input_data (dict): Input parameters

    Returns:
    - dict: Decision result
    """
    # Check required parameters
    required_params = ["sensor_distance", "threshold"]
    for param in required_params:
        if param not in input_data:
            return {"error": f"Missing required parameter: {param}"}

    try:
        sensor_distance = float(input_data["sensor_distance"])
        threshold = float(input_data["threshold"])

        # Decision logic
        if sensor_distance < threshold:
            action = "stop"
        else:
            action = "proceed"

        return {
            "action": action
        }

    except (ValueError, TypeError) as e:
        return {"error": f"Invalid parameter type: {str(e)}"}


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

        # Handle sensor fusion
        result = handle_sensor_fusion(input_data)

        # Output result as JSON
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))


if __name__ == "__main__":
    main()