"""
Summary: cdnEngine orchestrates CDN detection of domains.

Description: cdnEngine is a simple solution for detection
if a given domain or set of domains use a CDN.
"""

# Standard Python Libraries
import concurrent.futures
import math
import os
from typing import List, Tuple

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
            dom_in = detectCDN.Domain(
                dom, list(), list(), list(), list(), list(), list(), list()
            )
            self.domains.append(dom_in)


def chef_executor(
    domain: detectCDN.Domain,
    timeout: int,
    user_agent: str,
    verbosity: bool,
    interactive: bool,
    checks: str,
):
    """Attempt to make the method "threadsafe" by giving each worker its own detector."""
    # Define detector
    detective = detectCDN.cdnCheck()

    # Run checks
    try:
        detective.all_checks(
            # Timeout is split by .4 so that each chunk can only take less than half.
            domain,
            verbose=verbosity,
            timeout=math.ceil(timeout * 0.4),
            agent=user_agent,
            interactive=interactive,
            checks = checks,
        )
    except Exception as e:
        # Incase some uncaught error somewhere
        if interactive or verbosity:
            print(f"An unusual exception has occurred:\n{e}")
        return 1

    # Return 0 for success
    return 0


class Chef:
    """Chef will run analysis on the domains in the DomainPot."""

    def __init__(
        self,
        pot: DomainPot,
        threads: int,
        timeout: int,
        user_agent: str,
        interactive: bool = False,
        verbose: bool = False,
        checks: str = "chnw",
    ):
        """Give the chef the pot to use."""
        self.pot: DomainPot = pot
        self.pbar: tqdm = interactive
        self.verbose: bool = verbose
        self.timeout: int = timeout
        self.agent = user_agent
        self.interactive = interactive
        self.checks = checks

        # Determine thread count
        if threads and threads != 0:
            # Threads defined by user assign
            self.threads = threads
        else:
            # No user defined threads, get it from os.cpu_count()
            cpu_count = os.cpu_count()
            if cpu_count is None:
                cpu_count = 1
            self.threads = cpu_count  # type: ignore

    def grab_cdn(self, double: bool = False):  # type: ignore
        """Check for CDNs used be domain list."""
        # Use Concurrent futures to multithread with pools
        job_count = 0

        if self.verbose:
            # Give user information about the run:
            print(f"Using {self.threads} threads with a {self.timeout} second timeout")
            print(f"User Agent: {self.agent}\n")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.threads
        ) as executor:
            # If double, Double contents to combat CDN cache misses
            newpot = []
            if double:
                for domain in self.pot.domains:
                    newpot.append(domain)
            for domain in self.pot.domains:
                newpot.append(domain)
            job_count = len(newpot)
            # Setup pbar with correct amount size
            if self.pbar:
                pbar = tqdm(total=job_count)

            # Assign workers and assign to results list
            results = {
                executor.submit(
                    chef_executor,
                    domain,
                    self.timeout,
                    self.agent,
                    self.verbose,
                    self.interactive,
                    self.checks,
                )
                for domain in newpot
            }

            # Comb future objects for completed task pool.
            for future in concurrent.futures.as_completed(results):
                try:
                    # Try and grab feature result to dequeue job
                    future.result(timeout=self.timeout)
                except concurrent.futures.TimeoutError as e:
                    # Tell us we dropped it. Should log this instead.
                    if self.interactive or self.verbose:
                        print(f"Dropped due to: {e}")

                # Update status bar if allowed
                if self.pbar:
                    # We type ignore these as its "illegal" to access private attributes of an object
                    pending = f"Pending: {executor._work_queue.qsize()} jobs"  # type: ignore
                    threads = f"Threads: {len(executor._threads)}"  # type: ignore
                    pbar.set_description(f"[{pending}]==[{threads}]")
                    if self.pbar is not None:
                        pbar.update(1)
                    else:
                        pass

        # Return the amount of jobs done and error code
        return job_count

    def has_cdn(self):
        """For each domain, check if domain contains CDNS. If so, tick cdn_present to true."""
        for domain in self.pot.domains:
            if len(domain.cdns) > 0:
                domain.cdn_present = True

    def run_checks(self, double: bool = False) -> int:
        """Run analysis on the internal domain pool using detectCDN library."""
        cnt = self.grab_cdn(double)
        self.has_cdn()
        return cnt


def run_checks(
    domains: List[str],
    threads: int,
    timeout: int,
    user_agent: str,
    interactive: bool = False,
    verbose: bool = False,
    double: bool = False,
    checks: str = "chnw",
) -> Tuple[List[detectCDN.Domain], int]:
    """Orchestrate the use of DomainPot and Chef."""
    # Our domain pot
    dp = DomainPot(domains)

    # Our chef to manage pot
    chef = Chef(dp, threads, timeout, user_agent, interactive, verbose, checks)

    # Run analysis for all domains
    cnt = chef.run_checks(double)

    # Return all domains in form domain_pool, count of jobs processed, error code
    return (chef.pot.domains, cnt)
