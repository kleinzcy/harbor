#!/usr/bin/env python3
"""
Feature 6: Hardware Control
Maps steering predictions to serial commands for RC car control.
"""

import sys
import json


def map_prediction_to_command(prediction):
    """
    Map prediction value to hardware command.

    Parameters:
    - prediction (int): Prediction value (0-3)

    Returns:
    - str: Command string
    """
    # Map based on test cases and rc_driver_helper.py
    if prediction == 2:
        return "forward"
    elif prediction == 0:
        return "left"
    elif prediction == 1:
        return "right"
    elif prediction == 3:
        return "stop"
    else:
        # Default to stop for unknown predictions
        return "stop"


def handle_hardware_control(input_data):
    """
    Handle hardware control command mapping based on input.

    Parameters:
    - input_data (dict): Input parameters

    Returns:
    - dict: Command result
    """
    if "prediction" not in input_data:
        return {"error": "Missing prediction parameter"}

    try:
        prediction = int(input_data["prediction"])
        command = map_prediction_to_command(prediction)

        return {
            "command": command
        }

    except (ValueError, TypeError) as e:
        return {"error": f"Invalid prediction type: {str(e)}"}


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

        # Handle hardware control
        result = handle_hardware_control(input_data)

        # Output result as JSON
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))


if __name__ == "__main__":
    main()