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
from . import detectCDN

class DomainPot:
    def __init__(self, domains: List[str]):
        self.domains = []
        self.domain_to_cdn = {}

        # Convert to list of type domain
        for dom in domains:
            domin = detectCDN.domain(dom,
                                     list(),
                                     list(),
                                     list(),
                                     list(),
                                     list(),
                                     list(),
                                     list(),
                                     list())
            self.domains.append(domin)

class Chef:
    def __init__(self, pot: DomainPot=None):
        self.pot = pot
        self.frontable = {}

    """
    Check for CDNs used be domain list
    """
    def grab_cdn(self):
        # Checker module for each domain
        detective = detectCDN.cdnCheck()

        # Iterate over all domains and run checks
        for domain in self.pot.domains:
            detective.all_checks(domain) # Multithreading Point

    """
    For each domain, check if domain is frontable.
    CURRENT METRIC:
        - If domain has a CDN, it is frontable
    """
    def check_front(self):
        for domain in self.pot.domains:
            self.pot.domain_to_cdn[domain.url] = domain.cdns
        self.frontable = self.pot.domain_to_cdn

    """
    Run analysis on the internal domain pool
    """
    def run_checks(self):
        self.grab_cdn()
        self.check_front()

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

