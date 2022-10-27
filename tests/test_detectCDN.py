#!/usr/bin/env pytest -vs
"""Tests for detectCDN."""

# Third-Party Libraries
import dns.resolver

# cisagov Libraries
from findcdn.cdnEngine.detectCDN import Domain, cdnCheck

# Globals
TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"


def test_ip():
    """Test the IP resolving feature."""
    dns.resolver.default_resolver = dns.resolver.Resolver()
    dns.resolver.default_resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
    dom_in = Domain(
        "dns.google.com", list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.ip(dom_in)

    assert "8.8.8.8" in dom_in.ip, "the ip for dns.google.com should be 8.8.8.8"


def test_broken_ip():
    """Test a non-working domain IP resolving feature."""
    dns.resolver.default_resolver = dns.resolver.Resolver()
    dns.resolver.default_resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
    dom_in = Domain(
        "notarealdomain.fakedomaindne.com",
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
    )
    check = cdnCheck()
    return_code = check.ip(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_cname():
    """Test the CNAME resolving feature."""
    dom_in = Domain(
        "www.asu.edu", list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.cname(dom_in, timeout=TIMEOUT)

    assert (
        "pantheon-systems.map.fastly.net." in dom_in.cnames
    ), "www.asu.edu should have pantheon-systems.map.fastly.net. as a cname"


def test_broken_cname():
    """Test a non-working domain CNAME resolving feature."""
    dom_in = Domain(
        "notarealdomain.fakedomaindne.com",
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
    )
    check = cdnCheck()
    return_code = check.cname(dom_in, timeout=TIMEOUT)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_https_lookup():
    """Test the header resolving feature."""
    dom_in = Domain(
        "google.com", list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.https_lookup(
        dom_in, timeout=TIMEOUT, agent=USER_AGENT, interactive=False, verbose=False
    )

    assert "gws" in dom_in.headers, "google.com should have gws as a header"


def test_broken_https_lookup():
    """Test a non-working domain header resolving feature."""
    dom_in = Domain(
        "notarealdomain.fakedomaindne.com",
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
    )
    check = cdnCheck()
    check.https_lookup(
        dom_in, timeout=TIMEOUT, agent=USER_AGENT, interactive=False, verbose=False
    )
    assert len(dom_in.headers) <= 0, "There should be no response."


def test_whois():
    """Test the whois resolving feature."""
    dom_in = Domain(
        "google.com", list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.ip(dom_in)
    check.whois(dom_in, interactive=False, verbose=False)

    assert (
        "GOOGLE" in dom_in.whois_data
    ), "google.com should return GOOGLE in the whois_data"


def test_broken_whois():
    """Test a non-working domain whois resolving feature."""
    dom_in = Domain(
        "notarealdomain.fakedomaindne.com",
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
    )
    check = cdnCheck()
    check.ip(dom_in)
    return_code = check.whois(dom_in, interactive=False, verbose=False)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_all_checks():
    """Run all checks."""
    dom_in = Domain("login.gov", list(), list(), list(), list(), list(), list(), list())
    check = cdnCheck()
    check.all_checks(dom_in, timeout=TIMEOUT, agent=USER_AGENT)

    assert (
        ".cloudfront.net" in dom_in.cdns
    ), "the ip for dns.google.com should be 8.8.8.8"


def test_all_checks_by_name():
    """Run all checks and get CDN name."""
    dom_in = Domain("login.gov", list(), list(), list(), list(), list(), list(), list())
    check = cdnCheck()
    check.all_checks(dom_in, timeout=TIMEOUT, agent=USER_AGENT)

    assert (
        ".cloudfront.net" in dom_in.cdns
    ), "the ip for dns.google.com should be 8.8.8.8"


def test_all_checks_bad():
    """Test fake domain and ensure it dosen't break anything."""
    dns.resolver.default_resolver = dns.resolver.Resolver()
    dns.resolver.default_resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
    dom = Domain(
        "super.definitelynot.notarealdomain.fakedomaindne.com",
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
    )
    print(dom.url, dom.cdns, dom.cnames, dom.headers, dom.whois_data, dom.ip)
    check = cdnCheck()
    return_code = check.all_checks(dom, timeout=TIMEOUT, agent=USER_AGENT)
    print(return_code)
    print(dom.url, dom.cdns, dom.cnames, dom.headers, dom.whois_data, dom.ip)
    assert return_code != 0, "This fake site should return a non 0 code."
