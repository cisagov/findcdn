"""cdnengine library."""
# Ignoring mypy because this library does infact exist.
from . import detectcdn  # type: ignore
from .cdnengine import Chef, run_checks

# Define public exports
__all__ = ["Chef", "run_checks", "detectcdn"]
