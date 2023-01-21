"""
Summary: cdnEngine orchestrates CDN detection of domains.

Description: cdnEngine is a simple solution for detection
if a given domain or set of domains use a CDN.
"""

# Standard Python Libraries
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ContextDecorator
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, List

# Third-Party Libraries
from tqdm import tqdm
from loguru import logger
from validators import domain

# cisagov Libraries
# Internal Libraries
from findcdn.cdnEngine.analyzers import ANALYZERS
from findcdn.cdnEngine.analyzers.base import Domain


class functime(ContextDecorator):
    """Decorator to measure function time."""

    def __enter__(self):
        """Start timer definition."""
        self.start = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        """End timer and delta setting to elapsed."""
        self.end = perf_counter()
        self.elapsed = self.end - self.start


def analyze_domain(
    domain: str, checks: str, timeout: int = 10, verbose: bool = False
) -> Dict[str, Dict[str, object]]:
    """Analyze single domain."""
    error_code = 0
    dom = Domain(domain, [], [], [])
    results: List[str] = []

    # First identify if domain has valid IPs
    iplyzer = ANALYZERS["IPlyzer"]["class"]
    results, _, ec = iplyzer.run(dom, timeout)

    # If there are no results but there are IPs, that means
    # we must fallback to a different method for CDN detection.
    if not len(results) == 0 and len(dom.ips) > 0:
        # Sort analyzers based on priority (also filter out IPlyzer)
        analyzers = sorted(
            list(filter(lambda x: x != "IPlyzer", ANALYZERS.keys())),
            key=lambda x: ANALYZERS[x]["prio"],
        )

        # Filter out any with their arg missing
        analyzers = list(filter(lambda x: ANALYZERS[x]["arg"] in checks, analyzers))

        # Get results
        for analyzer in analyzers:
            a = ANALYZERS[analyzer]["class"]
            if verbose:
                logger.debug(f"[ANALYZER]::[{analyzer}] Starting..")
            results, _, ec = a.run(dom, timeout, verbose=verbose)
            if verbose:
                logger.debug(f"[ANALYZER]::[{analyzer}] RESULTS: {results} ERROR CODE: {error_code}")
            error_code |= ec
            if len(results) > 0:
                if verbose:
                    logger.debug(f"[ANALYZER]::[{analyzer}] CDN Has been found: {len(results) > 0 = }")
                break  # CDN has been found
            if ec == -1:
                break  # Domain just flat don't exist probably

    # Organize and return as dict
    dom_res = {}
    dom_res[dom.domain] = {
        "cdn": results,
        "ips": [str(ip) for ip in dom.ips],
        "has_cdn": 1 if len(results) > 0 else 0,
    }
    return dom_res


def analyze_domains(
    domains: List[str],
    checks: str,
    threads: int = 4,
    timeout: int = 10,
    verbose: bool = False,
    interactive: bool = False,
):
    """Perform analysis on multiple domains."""
    # Show loading bar if interactive
    if interactive:
        pbar = tqdm(total=len(domains))

    # This is so we can time the total execution of the code
    with functime() as ft:
        # Collect the subset of valid and invalid domains
        VALID_DOMAINS = list(filter(lambda x: domain(x), domains))
        INVALID_DOMAINS = list(filter(lambda x: not domain(x), domains))

        completed = []
        res = []

        # Thread pool executor for concurrent executions.
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit all the domains to be analyzed by a worker
            for domaind in VALID_DOMAINS:
                completed.append(
                    executor.submit(analyze_domain, domaind, checks, timeout, verbose)
                )

            # Wait for workers to finish
            for task in as_completed(completed):
                dom_res = task.result()
                res.append(dom_res)

                if verbose:
                    dom = list(dom_res.keys())[0]
                    found = dom_res[dom]['has_cdn']
                    logger.debug(f"{dom} {'has a cdn!' if found else 'has no cdn.'}")

                # Update progress bar as a result completes
                if interactive:
                    pbar.update(1)

    # Aggregate results
    results: Dict[str, Any] = {}
    results["valid_domains"] = {}
    [results["valid_domains"].update(dom) for dom in res]

    results["invalid_domains"] = [domain for domain in INVALID_DOMAINS]
    results["date"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    results["runtime"] = ft.elapsed
    results["total_analyzed"] = len(VALID_DOMAINS)
    results["count_with_cdn"] = sum(
        1 for _, v in results["valid_domains"].items() if v["has_cdn"]
    )

    return results
