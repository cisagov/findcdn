#!/usr/bin/env python3

"""
frontingEngine library gives the ability for a
simple solution for detection if a given domain
or set of domains are frontable.
"""

# Standard Python Libraries
from typing import List

# Third-Party Libraries


# Internal Libraries
from .frontingEngine_err import *
import detectCDN

class DomainPot:
    def __init__(self, domains: List[str]):
        self.domains = []
        self.domain_to_cdn = {}

        # Convert to list of type domain
        for domain in domains:
            self.domains.append(detectCDN.domain(domain))

class Chef:
    def __init__(self, pot: DomainPot=None):
        self.pot = pot
        self.frontable = {}

    """
    Check for CDNs used be domain list
    """
    def grab_cdn(self, domains: List[detectCDN.domain]):
        pass

    """
    For each domain, check if domain is frontable
    """
    def check_front(self, domains: List[detectCDN.domain]):
        pass

    """
    Run analysis on the internal domain pool
    """
    def run_checks(self):
        pass

def check_frontable(domains: List[str]):
    """This will orchestrate the use of DomainPot and Chef"""
    # Our domain pot
    dp = DomainPot(domains)

    # Our chef to manage pot
    chef = Chef(dp)

    # Run analysis for all domains
    chef.run_checks()

    # Return the set of frontable domains
    return chef.frontable



