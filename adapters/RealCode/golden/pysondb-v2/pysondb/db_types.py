"""
Type definitions for pysonDB-v2.
"""
from typing import TypedDict, Any, Dict, List, Union, Callable


# Database schema types
class DatabaseV2(TypedDict):
    version: int
    keys: List[str]
    data: Dict[str, Dict[str, Any]]


# Query function type
QueryFunc = Callable[[Dict[str, Any]], bool]

# ID generator type
IdGenerator = Callable[[], str]

# Supported value types
ValueType = Union[int, str, bool, list, dict, None]