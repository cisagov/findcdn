#!/usr/bin/env python3

"""
Summary: frontingEngine orchestrates frontability of domains.

Description: frontingEngine is a simple solution for detection
if a given domain or set of domains are frontable.
"""

# Standard Python Libraries
from typing import Dict, List

# Internal Libraries
from . import detectCDN


class DomainPot:
    """DomainPot defines the "pot" which Domain objects are stored."""

    def __init__(self, domains: List[str]):
        """Define the pot for the Chef to use."""
        self.domains = []
        self.domain_to_cdn: Dict[str, List] = {}

        # Convert to list of type domain
        for dom in domains:
            domin = detectCDN.Domain(
                dom, list(), list(), list(), list(), list(), list(), list(), list()
            )
            self.domains.append(domin)


class Chef:
    """Chef will run analysis on the domains in the DomainPot."""

    def __init__(self, pot: DomainPot = None):
        """Give the chef the pot to use."""
        self.pot = pot
        self.frontable: Dict[str, List] = {}

    def grab_cdn(self):
        """Check for CDNs used be domain list."""
        # Checker module for each domain
        detective = detectCDN.cdnCheck()

        # Iterate over all domains and run checks
        for domain in self.pot.domains:
            detective.all_checks(domain)  # Multithreading Point

    def check_front(self):
        """For each domain, check if domain is frontable using naive metric."""
        for domain in self.pot.domains:
            self.pot.domain_to_cdn[domain.url] = domain.cdns
        self.frontable = self.pot.domain_to_cdn

    def run_checks(self):
        """Run analysis on the internal domain pool."""
        self.grab_cdn()
        self.check_front()


def check_frontable(domains: List[str]):
    """Orchestrate the use of DomainPot and Chef."""
    # Our domain pot
    dp = DomainPot(domains)

    # Our chef to manage pot
    chef = Chef(dp)

    # Run analysis for all domains
    chef.run_checks()

    # Return the set of frontable domains
    return chef.frontable
