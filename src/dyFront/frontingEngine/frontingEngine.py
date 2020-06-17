#!/usr/bin/env python3

"""
Summary: frontingEngine orchestrates frontability of domains.

Description: frontingEngine is a simple solution for detection
if a given domain or set of domains are frontable.
"""

# Standard Python Libraries
import concurrent.futures
from typing import List

# Third-Party Libraries
from tqdm import tqdm

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

    def __init__(self, pot: DomainPot, pbar: tqdm = None, verbose: bool = False):
        """Give the chef the pot to use."""
        self.pot: DomainPot = pot
        self.pbar: tqdm = pbar
        self.verbose: bool = verbose

    def grab_cdn(self):
        """Check for CDNs used be domain list."""
        # Define detector
        detective = detectCDN.cdnCheck()

        # Use Concurrent futures to multithread with pools
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(
                detective.all_checks,
                self.pot.domains,
                [self.verbose for _ in self.pot.domains],
            )

            for _ in results:
                if self.pbar is not None:
                    self.pbar.update(1)

    def check_front(self):
        """For each domain, check if domain is frontable using naive metric."""
        for domain in self.pot.domains:
            if len(domain.cdns) > 0:
                domain.frontable = True

    def run_checks(self):
        """Run analysis on the internal domain pool."""
        self.grab_cdn()
        self.check_front()


def check_frontable(domains: List[str], pbar: tqdm = None, verbose: bool = False):
    """Orchestrate the use of DomainPot and Chef."""
    # Our domain pot
    dp = DomainPot(domains)

    # Our chef to manage pot
    chef = Chef(dp, pbar, verbose)

    # Run analysis for all domains
    chef.run_checks()

    # Return all domains for further parsing
    return chef.pot.domains
