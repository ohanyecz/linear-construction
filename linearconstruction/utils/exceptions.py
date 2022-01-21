"""This module contains exceptions for linearconstruction."""

__all__ = ["LinearConstructionException", "LinearConstructionDeprecationWarning"]


class LinearConstructionException(Exception):
    """Base exception class from which all exceptions should inherit."""
    ...


class LinearConstructionDeprecationWarning(LinearConstructionException):
    """An exception class to indicate a deprecated feature."""
    ...
