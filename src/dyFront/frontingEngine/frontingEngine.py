#!/usr/bin/env python3

"""
Summary: frontingEngine orchestrates frontability of domains.

Description: frontingEngine is a simple solution for detection
if a given domain or set of domains are frontable.
"""

# Standard Python Libraries
import concurrent.futures
import os
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


def chef_executor(domain: detectCDN.Domain, verbosity: bool = False):
    """Attempt to make the method "threadsafe" by giving each worker its own detector."""
    # Define detector
    detective = detectCDN.cdnCheck()

    # Run checks
    try:
        detective.all_checks(domain, verbosity)
    except BaseException:
        # Incase some uncaught error somewhere
        return 1

    # Return 0 for success
    return 0


class Chef:
    """Chef will run analysis on the domains in the DomainPot."""

    def __init__(self, pot: DomainPot, pbar: tqdm = None, verbose: bool = False):
        """Give the chef the pot to use."""
        self.pot: DomainPot = pot
        self.pbar: tqdm = pbar
        self.verbose: bool = verbose

    def grab_cdn(
        self, threads: int = min(32, os.cpu_count() + 4), double: bool = False  # type: ignore
    ):
        """Check for CDNs used be domain list."""
        # Use Concurrent futures to multithread with pools
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            # If double, Double contents to combat CDN cache misses
            newpot = []
            if double:
                for domain in self.pot.domains:
                    newpot.append(domain)
            for domain in self.pot.domains:
                newpot.append(domain)
            self.pbar = tqdm(total=len(newpot))

            # Assign workers and assign to results list
            results = {
                executor.submit(chef_executor, domain, self.verbose,)
                for domain in newpot
            }

            # Comb future objects for completed task pool.
            for future in concurrent.futures.as_completed(results):
                try:
                    # Try and grab feature result to dequeue job
                    future.result(timeout=30)
                except concurrent.futures.TimeoutError as e:
                    # Tell us we dropped it. Should log this instead.
                    print(f"Dropped due to: {e}")

                # Update status bar if allowed
                if self.pbar is not None:
                    pending = f"Pending: {executor._work_queue.qsize()} jobs"  # type: ignore
                    threads = f"Threads: {len(executor._threads)}"  # type: ignore
                    self.pbar.set_description(f"[{pending}]==[{threads}]")
                    if self.pbar is not None:
                        self.pbar.update(1)
                    else:
                        pass

    def check_front(self):
        """For each domain, check if domain is frontable using naive metric."""
        for domain in self.pot.domains:
            if len(domain.cdns) > 0:
                domain.frontable = True

    def run_checks(
        self, threads: int = min(32, os.cpu_count() + 4), double: bool = False  # type: ignore
    ):
        """Run analysis on the internal domain pool."""
        self.grab_cdn(threads, double)
        self.check_front()


def check_frontable(
    domains: List[str],
    pbar: tqdm = None,
    verbose: bool = False,
    threads: int = min(32, os.cpu_count() + 4),  # type: ignore
    double: bool = False,
):
    """Orchestrate the use of DomainPot and Chef."""
    # Our domain pot
    dp = DomainPot(domains)

    # Our chef to manage pot
    chef = Chef(dp, pbar, verbose)

    # Run analysis for all domains
    chef.run_checks(threads, double)

    # Return all domains for further parsing
    return chef.pot.domains
