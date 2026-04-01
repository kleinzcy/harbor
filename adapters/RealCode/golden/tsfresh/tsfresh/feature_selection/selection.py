"""
Feature selection functionality.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Tuple
from scipy import stats


def _calculate_p_values(
    X: pd.DataFrame,
    y: pd.Series,
    ml_task: str = "classification",
) -> Tuple[List[str], List[float]]:
    """
    Calculate p-values for each feature.

    Returns
    -------
    feature_names : List[str]
        List of feature names
    p_values : List[float]
        List of p-values for each feature
    """
    p_values = []
    features = []

    for col in X.columns:
        feature_values = X[col].values

        if ml_task == "classification":
            # For classification, use Mann-Whitney U test
            # Assume binary classification for now
            unique_classes = np.unique(y)
            if len(unique_classes) != 2:
                raise ValueError(
                    "Binary classification currently supported. "
                    "Found {} classes.".format(len(unique_classes))
                )

            class0_mask = y == unique_classes[0]
            class1_mask = y == unique_classes[1]

            values0 = feature_values[class0_mask]
            values1 = feature_values[class1_mask]

            # Remove NaN values
            values0 = values0[~np.isnan(values0)]
            values1 = values1[~np.isnan(values1)]

            if len(values0) == 0 or len(values1) == 0:
                p_value = 1.0
            else:
                try:
                    _, p_value = stats.mannwhitneyu(values0, values1)
                except ValueError:
                    p_value = 1.0

        elif ml_task == "regression":
            # For regression, use Spearman correlation
            # Remove NaN values
            valid_mask = ~np.isnan(feature_values) & ~np.isnan(y.values)
            if np.sum(valid_mask) < 2:
                p_value = 1.0
            else:
                try:
                    corr, p_value = stats.spearmanr(
                        feature_values[valid_mask], y.values[valid_mask]
                    )
                except ValueError:
                    p_value = 1.0
        else:
            raise ValueError(
                f"Unsupported ml_task: {ml_task}. "
                "Supported tasks: 'classification', 'regression'"
            )

        p_values.append(p_value)
        features.append(col)

    return features, p_values


def calculate_relevance_table(
    X: Union[pd.DataFrame, Dict[str, Any]],
    y: Union[pd.Series, List],
    fdr_level: float = 0.05,
    ml_task: str = "classification",
) -> pd.DataFrame:
    """
    Calculate relevance table with p-values and relevance flags.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns: feature, p_value, relevant
    """
    # Convert inputs if needed
    if isinstance(X, dict):
        X = pd.DataFrame(X)
    if isinstance(y, list):
        y = pd.Series(y)

    # Validate inputs
    if len(X) != len(y):
        raise ValueError("X and y must have the same number of samples")

    # Calculate p-values
    features, p_values = _calculate_p_values(X, y, ml_task)

    # Apply Benjamini-Yekutieli correction for multiple testing
    p_values_array = np.array(p_values)
    n_features = len(p_values_array)

    # Sort p-values
    sorted_indices = np.argsort(p_values_array)
    sorted_p_values = p_values_array[sorted_indices]

    # Calculate critical values
    # BY correction: c(m) = sum_{i=1}^m 1/i
    c_m = np.sum(1.0 / np.arange(1, n_features + 1))

    # Determine which features are relevant
    relevant_flags = [False] * n_features
    for i, p_val in enumerate(sorted_p_values):
        critical_value = (i + 1) * fdr_level / (n_features * c_m)
        if p_val <= critical_value:
            relevant_flags[sorted_indices[i]] = True

    # Create relevance table
    relevance_table = pd.DataFrame({
        "feature": features,
        "p_value": p_values,
        "relevant": relevant_flags,
    })

    return relevance_table


def select_features(
    X: Union[pd.DataFrame, Dict[str, Any]],
    y: Union[pd.Series, List],
    fdr_level: float = 0.05,
    ml_task: str = "classification",
) -> pd.DataFrame:
    """
    Select features that are statistically relevant to the target variable.

    Parameters
    ----------
    X : pandas.DataFrame or dict
        Feature matrix with samples as rows and features as columns.
    y : pandas.Series or list
        Target variable.
    fdr_level : float, default 0.05
        False Discovery Rate level for multiple testing correction.
    ml_task : str, default "classification"
        Machine learning task type. Currently supports "classification"
        and "regression".

    Returns
    -------
    pandas.DataFrame
        DataFrame containing only selected features that pass the
        significance threshold.
    """
    # Calculate relevance table
    relevance_table = calculate_relevance_table(X, y, fdr_level, ml_task)

    # Get relevant features
    relevant_features = relevance_table[
        relevance_table["relevant"]
    ]["feature"].tolist()

    # Convert X to DataFrame if dict
    if isinstance(X, dict):
        X = pd.DataFrame(X)

    # Return DataFrame with only selected features
    if relevant_features:
        return X[relevant_features].copy()
    else:
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=relevant_features)