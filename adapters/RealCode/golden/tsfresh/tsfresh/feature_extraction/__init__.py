"""
Feature extraction module for time series data.
"""

from .extraction import extract_features
from .settings import MinimalFCParameters, ComprehensiveFCParameters

__all__ = [
    "extract_features",
    "MinimalFCParameters",
    "ComprehensiveFCParameters",
]