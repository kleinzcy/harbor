# tsfresh - Time Series Feature Extraction Library

## Project Goal

Build a Python library for automated time series feature extraction and selection that allows developers to extract hundreds of statistical, spectral, and nonlinear features from time series data without manually implementing complex feature engineering pipelines. The library will provide statistically rigorous feature selection methods to identify relevant features for machine learning tasks, supporting both supervised and unsupervised learning scenarios.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import pandas as pd
from tsfresh import extract_features, select_features

# Create sample time series data
data = pd.DataFrame({
    "id": [1, 1, 1, 2, 2, 2],
    "time": [0, 1, 2, 0, 1, 2],
    "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
})

# Extract features
features = extract_features(data, column_id="id", column_sort="time", column_value="value")
print(features)

# Select relevant features (example with dummy target)
X = features
y = pd.Series([0, 1])  # Binary target
selected_features = select_features(X, y, ml_task="classification")
print(selected_features)
```

## Features

### 1. Automated Feature Extraction

Extract hundreds of features from time series data with a single function call.

### 2. Intelligent Feature Selection

Automatically select features that are statistically relevant to your target variable.

### 3. Special Structure Handling

Handle multivariate time series, irregular sampling, and event sequences.

### 4. Comprehensive API and CLI Interface

Use through Python API or command-line interface.

### 5. Modular and Extensible Architecture

Easy to extend with custom feature calculators.

## Documentation

For detailed documentation, please refer to the [official documentation](https://tsfresh.readthedocs.io/).

## License

MIT