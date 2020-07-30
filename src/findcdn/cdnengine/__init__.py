"""cdnengine library."""
# Ignoring mypy because this library does infact exist.
from . import detectcdn  # type: ignore
from .cdnengine import Chef, DomainPot, run_checks

# Define public exports
__all__ = ["DomainPot", "Chef", "run_checks", "detectcdn"]
