#!/usr/bin/env python3

"""Define public exports."""
__all__ = ["NoIPaddress"]


class NoIPaddress(Exception):
    """Raise when no IP addresses in domain class."""

    def __init__(self, message="There are no IP addresses to check!"):
        """Instantiate super class with passed message."""
        self.message = message
        super().__init__(self.message)
