"""
pytz - Python Timezone Handling Library
========================================

This library provides timezone handling using the IANA (Olson) timezone database.
"""

__version__ = "2024.1"
VERSION = __version__
OLSON_VERSION = "2024a"

# Import the main public API
from .lazy import LazyList, LazySet, LazyDict
from .exceptions import (
    UnknownTimeZoneError, 
    AmbiguousTimeError, 
    NonExistentTimeError
)
from .tzinfo import (
    timezone,
    utc,
    UTC,
    FixedOffset,
    country_timezones,
    all_timezones,
    common_timezones,
    all_timezones_set,
)

# Make these available at the module level
__all__ = [
    'timezone',
    'utc',
    'UTC',
    'FixedOffset',
    'country_timezones',
    'all_timezones',
    'common_timezones',
    'all_timezones_set',
    'UnknownTimeZoneError',
    'AmbiguousTimeError',
    'NonExistentTimeError',
    'LazyList',
    'LazySet',
    'LazyDict',
    '__version__',
    'VERSION',
    'OLSON_VERSION',
]