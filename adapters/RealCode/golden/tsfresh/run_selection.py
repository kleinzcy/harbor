#!/usr/bin/env python
"""
Script for feature selection testing.
Reads JSON from stdin, outputs results to stdout.
"""

import sys
import json
import pandas as pd
from tsfresh.feature_selection import select_features, calculate_relevance_table


def main():
    # Read JSON from stdin
    input_data = json.load(sys.stdin)

    # Parse input
    X = input_data.get("X")
    y = input_data.get("y")
    fdr_level = input_data.get("fdr_level", 0.05)
    ml_task = input_data.get("ml_task", "classification")

    # Convert X to DataFrame if dict
    if isinstance(X, dict):
        X = pd.DataFrame(X)

    # Calculate relevance table
    relevance_table = calculate_relevance_table(X, y, fdr_level, ml_task)

    # Get selected features
    selected = select_features(X, y, fdr_level, ml_task)
    selected_features = selected.columns.tolist()

    # Prepare output
    output = {
        "selected_features": selected_features,
        "relevance_table": relevance_table.to_dict(orient="records"),
    }

    # Output JSON
    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()