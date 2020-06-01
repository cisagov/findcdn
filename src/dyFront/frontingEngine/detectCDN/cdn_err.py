#!/usr/bin/env python3

"""
Define public exports.
"""
__all__ = ["NoDomains",
           "NoIPaddress"]

class NoDomains(Exception):
    """Raised when no domains exist in CDN Check"""
    def __init__(self, message="There are no Domains to check!"):
        self.message = message
        super().__init__(self.message)

class NoIPaddress(Exception):
    """Raised when no IP addresses in domain class"""
    def __init__(self, message="There are no IP addresses to check!"):
        self.message = message
        super().__init__(self.message)
