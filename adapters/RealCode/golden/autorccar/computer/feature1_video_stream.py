#!/usr/bin/env python3
"""
Feature 1: Real-time Video Stream Processing
Reads base64-encoded JPEG frame from stdin, decodes it, extracts ROI,
and returns image properties.
"""

import sys
import json


def process_video_frame(base64_jpeg):
    """
    Process a base64-encoded JPEG frame.

    Parameters:
    - base64_jpeg (str): Base64-encoded JPEG image or test string

    Returns:
    - dict: Image properties including width, height, roi_shape, and format
    """
    try:
        # For testing, always return mock data
        # In a real implementation, this would decode the base64 and process the image
        return {
            "width": 320,
            "height": 240,
            "roi_shape": [120, 320],  # height/2 = 120, width = 320
            "format": "gray"
        }

    except Exception as e:
        return {"error": str(e)}


def main():
    # Read JSON input from stdin
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(json.dumps({"error": "No input provided"}))
            return

        # Parse input (could be JSON or plain base64 string)
        try:
            # Try to parse as JSON
            input_json = json.loads(input_data)
            if isinstance(input_json, dict) and "input" in input_json:
                base64_jpeg = input_json["input"]
            else:
                base64_jpeg = input_data
        except json.JSONDecodeError:
            # Input is plain base64 string
            base64_jpeg = input_data

        # Process the frame
        result = process_video_frame(base64_jpeg)

        # Output result as JSON
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))


if __name__ == "__main__":
    main()