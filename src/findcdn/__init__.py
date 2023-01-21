"""The findcdn library."""
# We disable a Flake8 check for "Module imported but unused (F401)" here because
# although this import is not directly used, it populates the value
# package_name.__version__, which is used to get version information about this
# Python package.
from ._version import __version__  # noqa: F401

# from .findcdn import interactive, main
# from .findcdn_err import FileWriteError, InvalidDomain, OutputFileExists
from .cdnEngine import analyze_domain, analyze_domains

__all__ = [
    "main",
    "__version__",
    "interactive",
    "analyze_domain",
    "analyze_domains",
]
