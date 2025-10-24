# src/__init__.py

from __future__ import annotations
import logging

"""
trader package

Basic package initialization: exposes package version and a logger.
"""

__all__ = ["__version__", "get_version", "logger"]

# Get package version if installed; fall back to a sensible default when developing.
try:
    from importlib.metadata import version, PackageNotFoundError  # Python 3.8+
except Exception:
    # If running on older Python with importlib-metadata backport available
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

try:
    __version__ = version("trader")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

# Lightweight logger for the package. Do not configure handlers here to avoid
# interfering with application logging configuration.

logger = logging.getLogger("trader")


def get_version() -> str:
    """Return the package version."""
    return __version__