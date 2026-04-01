# tsfresh - Time Series Feature Extraction Library

## Project Goal

Build a Python library for automated time series feature extraction and selection that allows developers to extract hundreds of statistical, spectral, and nonlinear features from time series data without manually implementing complex feature engineering pipelines. The library will provide statistically rigorous feature selection methods to identify relevant features for machine learning tasks, supporting both supervised and unsupervised learning scenarios.

---

## Background & Problem

Without this library/tool, developers are forced to manually implement time series feature extraction algorithms, which involves writing repetitive boilerplate code for basic statistical features (mean, variance, peaks) and complex features (spectral analysis, time reversal symmetry). This leads to error-prone implementations, inconsistent feature definitions, and significant maintenance overhead when dealing with multivariate time series, irregular sampling, or event sequences.

With this library/tool, developers can automatically extract hundreds of features with a single function call, apply statistically sound feature selection to avoid overfitting, and seamlessly integrate time series feature engineering into their machine learning workflows through scikit-learn compatibility.

---

## Core Features

### Feature 1: Automated Feature Extraction

**As a data scientist**, I want to automatically extract hundreds of features from time series data, so I can quickly generate comprehensive feature sets for machine learning models without manual implementation.

**Expected Behavior / Usage:**

The `extract_features()` function should accept time series data in pandas DataFrame or dictionary format, along with column identifiers for ID, timestamp, and value. It should compute a configurable set of features (basic statistics, spectral features, nonlinear dynamics) and return a pandas DataFrame where rows correspond to time series IDs and columns correspond to extracted features.

**Test Cases:** `tests/test_cases/feature1_extraction.json`

```json
{
    "description": "Extract basic statistical features from a simple time series",
    "cases": [
        {
            "input": {
                "data": {"id": [1, 1, 1], "time": [0, 1, 2], "value": [1.0, 2.0, 3.0]},
                "column_id": "id",
                "column_sort": "time",
                "column_value": "value",
                "default_fc_parameters": "minimal"
            },
            "expected_output": {
                "columns": ["value__mean", "value__variance", "value__length"],
                "1": [2.0, 1.0, 3.0]
            }
        },
        {
            "input": {
                "data": {"id": [1, 1, 2, 2], "time": [0, 1, 0, 1], "value": [1.0, 2.0, 3.0, 4.0]},
                "column_id": "id",
                "column_sort": "time",
                "column_value": "value",
                "default_fc_parameters": "minimal"
            },
            "expected_output": {
                "columns": ["value__mean", "value__variance", "value__length"],
                "1": [1.5, 0.5, 2.0],
                "2": [3.5, 0.5, 2.0]
            }
        }
    ]
}
```

---

### Feature 2: Intelligent Feature Selection

**As a machine learning engineer**, I want to automatically select features that are statistically relevant to my target variable, so I can reduce dimensionality and avoid overfitting while maintaining model performance.

**Expected Behavior / Usage:**

The `select_features()` function should accept a feature matrix (DataFrame) and target variable (Series), perform statistical hypothesis tests (Mann-Whitney U, Fisher exact, etc.) with multiple testing corrections (Benjamini-Yekutieli), and return a DataFrame containing only features that pass the significance threshold. The function should support classification, regression, and unsupervised tasks.

**Test Cases:** `tests/test_cases/feature2_selection.json`

```json
{
    "description": "Select features relevant to a binary target variable",
    "cases": [
        {
            "input": {
                "X": {"feature1": [1.0, 2.0, 3.0, 4.0], "feature2": [0.1, 0.2, 0.3, 0.4], "feature3": [10, 20, 30, 40]},
                "y": [0, 0, 1, 1],
                "fdr_level": 0.05,
                "ml_task": "classification"
            },
            "expected_output": {
                "selected_features": ["feature1", "feature3"],
                "relevance_table": [
                    {"feature": "feature1", "p_value": 0.02, "relevant": true},
                    {"feature": "feature2", "p_value": 0.8, "relevant": false},
                    {"feature": "feature3", "p_value": 0.01, "relevant": true}
                ]
            }
        }
    ]
}
```

---

### Feature 3: Special Structure Handling

**As a data engineer**, I want to handle complex time series structures like multivariate data, event sequences, and irregular sampling, so I can apply feature extraction to real-world datasets without extensive preprocessing.

**Expected Behavior / Usage:**

*3.1 Multivariate Time Series Support — Handle multiple variables per time series ID*

The library should support a `column_kind` parameter to distinguish different variables within the same time series. Feature extraction should be applied per variable kind, with results combined into a single feature matrix.

**Test Cases:** `tests/test_cases/feature3_1_multivariate.json`

```json
{
    "description": "Extract features from multivariate time series with temperature and pressure measurements",
    "cases": [
        {
            "input": {
                "data": {"id": [1, 1, 1, 1], "time": [0, 1, 0, 1], "kind": ["temp", "temp", "pressure", "pressure"], "value": [20.0, 21.0, 100.0, 101.0]},
                "column_id": "id",
                "column_sort": "time",
                "column_kind": "kind",
                "column_value": "value"
            },
            "expected_output": {
                "columns": ["temp__mean", "temp__variance", "pressure__mean", "pressure__variance"],
                "1": [20.5, 0.5, 100.5, 0.5]
            }
        }
    ]
}
```

*3.2 Irregular Sampling and Event Sequences — Handle non-uniform time intervals and event data*

The library should support irregularly sampled time series and event sequences by using appropriate feature calculators that don't assume uniform spacing.

**Test Cases:** `tests/test_cases/feature3_2_irregular.json`

```json
{
    "description": "Extract features from irregularly sampled time series",
    "cases": [
        {
            "input": {
                "data": {"id": [1, 1, 1], "time": [0, 2.5, 5.0], "value": [1.0, 2.0, 3.0]},
                "column_id": "id",
                "column_sort": "time",
                "column_value": "value"
            },
            "expected_output": {
                "columns": ["value__mean", "value__variance", "value__time_stretch"],
                "1": [2.0, 1.0, 0.5]
            }
        }
    ]
}
```

---

### Feature 4: Comprehensive API and CLI Interface

**As a developer**, I want to use the library through both Python API and command-line interfaces, so I can integrate it into scripts, notebooks, and production pipelines.

**Expected Behavior / Usage:**

The library should provide a clean Python API with functions like `extract_features()`, `select_features()`, and `extract_relevant_features()`. Additionally, command-line scripts should allow batch processing of CSV/JSON files with configurable parameters.

**Test Cases:** `tests/test_cases/feature4_interface.json`

```json
{
    "description": "Command-line interface for feature extraction from CSV file",
    "cases": [
        {
            "input": {
                "command": "tsfresh-extract-features --input data.csv --id-column id --time-column time --value-column value --output features.csv",
                "input_file": "id,time,value\n1,0,1.0\n1,1,2.0\n2,0,3.0\n2,1,4.0"
            },
            "expected_output": {
                "output_file_columns": ["id", "value__mean", "value__variance"],
                "row_count": 2
            }
        }
    ]
}
```

---

### Feature 5: Examples and Evaluation Suite

**As a new user**, I want to access example code and test cases, so I can quickly understand how to use the library for common time series analysis tasks.

**Expected Behavior / Usage:**

The library should include Jupyter notebooks demonstrating feature extraction and selection workflows, along with a comprehensive test suite that validates all feature calculators and selection methods.

**Test Cases:** `tests/test_cases/feature5_examples.json`

```json
{
    "description": "Example notebook generates expected output for sample dataset",
    "cases": [
        {
            "input": {
                "notebook": "01_feature_extraction.ipynb",
                "dataset": "robot_execution_failures"
            },
            "expected_output": {
                "extracted_features_shape": [100, 50],
                "selected_features_count": 15
            }
        }
    ]
}
```

---

### Feature 6: Modular and Extensible Architecture

**As a library maintainer**, I want a well-structured package with clear dependencies and installation process, so users can easily install, extend, and integrate the library into their projects.

**Expected Behavior / Usage:**

The library should be packaged as a standard Python package with `setup.py` declaring dependencies (pandas, numpy, scipy, scikit-learn, statsmodels, etc.) and entry points for CLI tools. The codebase should be modular with separate modules for feature extraction, feature selection, utilities, and transformers, allowing users to import specific components. Users should be able to add custom feature calculators through a registration mechanism.

**Test Cases:** `tests/test_cases/feature6_package.json`

```json
{
    "description": "Package installation and basic import test",
    "cases": [
        {
            "input": {
                "command": "pip install -e ."
            },
            "expected_output": {
                "exit_code": 0,
                "module_imports": ["tsfresh", "tsfresh.feature_extraction", "tsfresh.feature_selection"]
            }
        },
        {
            "input": {
                "command": "python -c 'from tsfresh import extract_features; from tsfresh.feature_extraction import MinimalFCParameters; print(\"OK\")'"
            },
            "expected_output": {
                "stdout": "OK"
            }
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_extraction.json` should write its output to `tests/stdout/feature1_extraction@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.