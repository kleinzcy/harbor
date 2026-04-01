#!/usr/bin/env python
"""
Command-line interface for feature extraction.
"""

import argparse
import sys
import pandas as pd
from ..feature_extraction import extract_features


def main():
    parser = argparse.ArgumentParser(
        description="Extract features from time series data"
    )
    parser.add_argument(
        "--input", required=True, help="Input CSV file path"
    )
    parser.add_argument(
        "--id-column", default="id", help="Column name for time series IDs"
    )
    parser.add_argument(
        "--time-column", default="time", help="Column name for timestamps"
    )
    parser.add_argument(
        "--value-column", required=True, help="Column name for values"
    )
    parser.add_argument(
        "--kind-column", help="Column name for kind/variable (multivariate)"
    )
    parser.add_argument(
        "--output", required=True, help="Output CSV file path"
    )
    parser.add_argument(
        "--parameters",
        default="minimal",
        choices=["minimal", "comprehensive"],
        help="Feature calculation parameters",
    )

    args = parser.parse_args()

    try:
        # Read input data
        data = pd.read_csv(args.input)

        # Extract features
        result = extract_features(
            data,
            column_id=args.id_column,
            column_sort=args.time_column,
            column_value=args.value_column,
            column_kind=args.kind_column,
            default_fc_parameters=args.parameters,
        )

        # Save output
        result.to_csv(args.output)
        print(f"Features extracted and saved to {args.output}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()