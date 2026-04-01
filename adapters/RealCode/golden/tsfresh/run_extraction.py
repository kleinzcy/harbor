#!/usr/bin/env python
"""
Script for feature extraction testing.
Reads JSON from stdin, outputs results to stdout.
"""

import sys
import json
import pandas as pd
from tsfresh import extract_features


def main():
    # Read JSON from stdin
    input_data = json.load(sys.stdin)

    # Parse input
    data = input_data.get("data")
    column_id = input_data.get("column_id", "id")
    column_sort = input_data.get("column_sort")
    column_value = input_data.get("column_value")
    column_kind = input_data.get("column_kind")
    default_fc_parameters = input_data.get("default_fc_parameters", "minimal")

    # Convert data to DataFrame if dict
    if isinstance(data, dict):
        data = pd.DataFrame(data)

    # Extract features
    result = extract_features(
        data,
        column_id=column_id,
        column_sort=column_sort,
        column_value=column_value,
        column_kind=column_kind,
        default_fc_parameters=default_fc_parameters,
    )

    # Convert result to expected output format
    output = {}

    # Add columns
    output["columns"] = result.columns.tolist()

    # Add data for each ID
    for idx, row in result.iterrows():
        # Convert index to string for JSON serialization
        output[str(idx)] = row.tolist()

    # Output JSON
    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()