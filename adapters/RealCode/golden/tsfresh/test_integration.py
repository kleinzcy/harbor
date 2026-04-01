#!/usr/bin/env python
"""Quick integration test."""

import pandas as pd
from tsfresh import extract_features, select_features

print("Testing feature extraction...")
data = pd.DataFrame({
    "id": [1, 1, 1, 2, 2, 2],
    "time": [0, 1, 2, 0, 1, 2],
    "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
})

features = extract_features(data, column_id="id", column_sort="time", column_value="value")
print(f"Features shape: {features.shape}")
print(f"Features columns: {features.columns.tolist()}")
print(f"Features:\n{features}")

print("\nTesting feature selection...")
X = features
y = pd.Series([0, 1])  # Binary target
selected = select_features(X, y, ml_task="classification")
print(f"Selected features shape: {selected.shape}")
print(f"Selected features: {selected.columns.tolist()}")

print("\nTesting multivariate...")
data_multi = pd.DataFrame({
    "id": [1, 1, 1, 1],
    "time": [0, 1, 0, 1],
    "kind": ["temp", "temp", "pressure", "pressure"],
    "value": [20.0, 21.0, 100.0, 101.0]
})

features_multi = extract_features(
    data_multi,
    column_id="id",
    column_sort="time",
    column_kind="kind",
    column_value="value"
)
print(f"Multivariate features shape: {features_multi.shape}")
print(f"Multivariate features columns: {features_multi.columns.tolist()}")

print("\nAll tests passed!")