#!/usr/bin/env python3

"""
Summary: frontingEngine orchestrates frontability of domains.

Description: frontingEngine is a simple solution for detection
if a given domain or set of domains are frontable.
"""

# Standard Python Libraries
import queue
import threading
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


class ChefWorker(threading.Thread):
    """ChefWorker defines the thread worker for the Chef class."""

    def __init__(self, q: queue.Queue, tid: int, pbar: tqdm):
        """Define the thread. Inherit from super class."""
        threading.Thread.__init__(self)
        self.queue = q
        self.tid = tid
        self.pbar = pbar

    def run(self):
        """Run the thread and check domain for domain object."""
        # Try to grab from queue
        try:
            domain = self.queue.get(timeout=1)
        except queue.Empty:
            return

        # Create our detector object
        detective = detectCDN.cdnCheck()

        # Detect CDN
        detective.all_checks(domain)

        # Signal complete and update status
        self.queue.task_done()
        self.pbar.update(1)


class Chef:
    """Chef will run analysis on the domains in the DomainPot."""

    def __init__(self, pot: DomainPot):
        """Give the chef the pot to use."""
        self.pot: DomainPot = pot

    def grab_cdn(self):
        """Check for CDNs used be domain list."""
        # Setup Status bar
        total_domains = 0
        for domain in self.pot.domains:
            total_domains += 1
        pbar = tqdm(total=total_domains)

        # Define queue
        q = queue.Queue()

        # Set number of threads
        threads = list()
        for tid in range(1, 40):
            worker = ChefWorker(q, tid, pbar)
            worker.setDaemon(True)
            worker.start()
            threads.append(worker)

        # Populate queue
        for domain in self.pot.domains:
            q.put(domain)
        q.join()

        # Wait for threads to exit
        for thread in threads:
            thread.join()
        pbar.close()

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
