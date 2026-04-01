"""
unittest-parametrize: Parameterized testing for unittest framework.

Provides a decorator-based API similar to pytest.mark.parametrize for unittest.
"""

__version__ = "1.0.0"
__all__ = ["parametrize", "ParametrizedTestCase", "param"]

from .decorators import parametrize
from .testcase import ParametrizedTestCase
from .param import param