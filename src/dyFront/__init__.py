"""The dyFront library."""
from ._version import __version__  # noqa: F401
from .dyFront import interactive, main

__all__ = ["main", "__version__", "interactive"]
