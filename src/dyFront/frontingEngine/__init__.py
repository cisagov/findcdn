"""frontingEngine library."""
from . import detectCDN
from .frontingEngine import Chef, DomainPot, check_frontable

"""Define public exports."""
__all__ = ["DomainPot", "Chef", "check_frontable", "detectCDN"]
