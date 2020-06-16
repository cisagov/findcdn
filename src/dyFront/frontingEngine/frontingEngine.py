#!/usr/bin/env python3

"""
Summary: frontingEngine orchestrates frontability of domains.

Description: frontingEngine is a simple solution for detection
if a given domain or set of domains are frontable.
"""

# Standard Python Libraries
import threading
from typing import List

# Internal Libraries
from . import detectCDN


class DomainPot:
    """DomainPot defines the "pot" which Domain objects are stored."""

    def __init__(self, domains: List[str]):
        """Define the pot for the Chef to use."""
        self.domains: List[detectCDN.Domain] = []

        # Convert to list of type domain
        for dom in domains:
            domin = detectCDN.Domain(
                dom, list(), list(), list(), list(), list(), list(), list()
            )
            self.domains.append(domin)


class Chef:
    """Chef will run analysis on the domains in the DomainPot."""

    def __init__(self, pot: DomainPot):
        """Give the chef the pot to use."""
        self.pot: DomainPot = pot

    def grab_cdn(self):
        """Check for CDNs used be domain list."""
        # Checker module for each domain
        detective = detectCDN.cdnCheck()

        # Iterate over all domains and run checks
        threads = list()
        for domain in self.pot.domains:
            detective.all_checks(domain)
            x = threading.Thread(
                target=detective.all_checks, args=(domain,), daemon=True
            )  # Multithreading Point
            threads.append(x)
            x.start()
        for _, thread in enumerate(threads):
            thread.join()

    def check_front(self):
        """For each domain, check if domain is frontable using naive metric."""
        for domain in self.pot.domains:
            if len(domain.cdns) > 0:
                domain.frontable = True

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

    # Return all domains for further parsing
    return chef.pot.domains
