<<<<<<< HEAD:src/findcdn/__init__.py
"""The findcdn library."""
=======
"""The example library."""

>>>>>>> 272917ac0cd708e1201cbefb6824e84fa777dabd:src/example/__init__.py
# We disable a Flake8 check for "Module imported but unused (F401)" here because
# although this import is not directly used, it populates the value
# package_name.__version__, which is used to get version information about this
# Python package.
from ._version import __version__  # noqa: F401
from .findcdn import interactive, main
from .findcdn_err import FileWriteError, InvalidDomain, OutputFileExists

__all__ = [
    "main",
    "__version__",
    "interactive",
    "OutputFileExists",
    "InvalidDomain",
    "FileWriteError",
]
