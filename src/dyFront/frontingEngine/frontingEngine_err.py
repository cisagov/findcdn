#!/usr/bin/env python3

"""
Define public exports.
"""
__all__ = ["DomainsExist"]

class DomainsExist(Exception):
    """Raised when the self.domains list is not empty."""
    def __init__(self, message="Domains list not empty!"):
        self.message - message
        super().__init__(self.message)

