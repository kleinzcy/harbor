"""
Exception classes for pytz.
"""


class UnknownTimeZoneError(KeyError):
    """Exception raised when a timezone name is not found."""
    pass


class AmbiguousTimeError(ValueError):
    """Exception raised when a local time is ambiguous during DST transition."""
    pass


class NonExistentTimeError(ValueError):
    """Exception raised when a local time does not exist during DST transition."""
    pass