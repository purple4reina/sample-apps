class SealVersionsException(Exception):
    """Base class for exceptions in this module."""


class ValidationException(SealVersionsException):
    """Exception raised for bad input data"""


class InconsistentVersionException(ValidationException):
    """Exception raised when the version of a package is inconsistent."""


class MissingVersionValue(ValidationException):
    """Exception raised when some fields are missing."""


class BadVersionFormatException(ValidationException):
    """Exception raised when the version of a package does not match our regex format."""
