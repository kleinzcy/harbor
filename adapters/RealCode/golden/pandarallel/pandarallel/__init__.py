"""
Pandarallel - Simple and efficient parallelization tool for pandas
"""

__version__ = "1.0.0"
__author__ = "Pandarallel Team"

from .config import PandarallelConfig, initialize
from .monkey_patch import patch_all, unpatch_all

__all__ = [
    "PandarallelConfig",
    "initialize",
    "patch_all",
    "unpatch_all",
]