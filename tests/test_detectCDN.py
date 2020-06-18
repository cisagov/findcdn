#!/usr/bin/env pytest -vs
"""Tests for detectCDN."""

# Third-Party Libraries
import dns.resolver
import pytest

# cisagov Libraries
from dyFront.frontingEngine.detectCDN import Domain, cdnCheck


def test_ip():
    """Test the IP resolving feature."""
    dns.resolver.default_resolver = dns.resolver.Resolver()
    dns.resolver.default_resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
    dom_in = Domain(
        "dns.google.com", list(), list(), list(), list(), list(), list(), list(), list()
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
        list(),
    )
    check = cdnCheck()
    return_code = check.ip(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


@pytest.mark.skipif(
    'os.getenv("CENSYS_SECRET") == None or os.getenv("CENSYS_UID") == None',
    reason="Environment var not set",
)
def test_censys_bad_domain():
    """Non-working domain to test censys feature with."""
    dom_in = Domain("wewewewewewewewe.com")
    check = cdnCheck()
    result = check.censys(dom_in)

    # Assertions
    assert result == 2, "Censys should not return data."


@pytest.mark.skipif(
    'os.getenv("CENSYS_SECRET") == None or os.getenv("CENSYS_UID") == None',
    reason="Environment var not set",
)
def test_censys_check_uid_secret():
    """Check if system variables correctly grabbed."""
    check = cdnCheck()
    assert check.UID is not None, "UID Needs to be defined to use Censys."
    assert check.SECRET is not None, "SECRET Needs to be defined to use Censys."

    # Set these to None
    check.UID = None
    check.SECRET = None

    result = check.censys
    assert result != 1, "Method should not run if UID and SECRET are not defined."


@pytest.mark.skipif(
    'os.getenv("CENSYS_SECRET") == None or os.getenv("CENSYS_UID") == None',
    reason="Environment var not set",
)
def test_censys():
    """Check basic functionality of the censys module."""
    dom_in = Domain(
        "amazon.com",
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
    )
    check = cdnCheck()
    check.censys(dom_in)

    # Assertions
    assert len(dom_in.censys_data) > 0, "Data should be returned for known good data."

    # Test for our intended data inside the returned data
    data_found = False
    for data in dom_in.censys_data:
        if "cloudfront" in data:
            data_found = True
    assert data_found, "Data returned does not match known data of amazon.com."


def test_cname():
    """Test the CNAME resolving feature."""
    dom_in = Domain(
        "www.asu.edu", list(), list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.cname(dom_in)

    assert (
        "www.asu.edu.cdn.cloudflare.net." in dom_in.cnames
    ), "www.asu.edu should have www.asu.edu.cdn.cloudflare.net. as a cname"


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
        list(),
    )
    check = cdnCheck()
    return_code = check.cname(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_namesrv():
    """Test the namesrv resolving feature."""
    dom_in = Domain(
        "google.com", list(), list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.namesrv(dom_in)

    assert (
        "ns1.google.com." in dom_in.namesrvs
    ), "google.com should have ns1.google.com. as a nameserver"


def test_broken_namesrv():
    """Test a non-working domain namesrv resolving feature."""
    dom_in = Domain(
        "notarealdomain.fakedomaindne.com",
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
        list(),
    )
    check = cdnCheck()
    return_code = check.namesrv(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_https_lookup():
    """Test the header resolving feature."""
    dom_in = Domain(
        "google.com", list(), list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.https_lookup(dom_in)

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
        list(),
    )
    check = cdnCheck()
    check.https_lookup(dom_in)
    assert len(dom_in.headers) <= 0, "There should be no response."


def test_whois():
    """Test the whois resolving feature."""
    dom_in = Domain(
        "google.com", list(), list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.ip(dom_in)
    check.whois(dom_in)

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
        list(),
    )
    check = cdnCheck()
    check.ip(dom_in)
    return_code = check.whois(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_all_checks():
    """Run all checks."""
    dom_in = Domain(
        "login.gov", list(), list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.all_checks(dom_in)

    assert (
        ".cloudfront.net" in dom_in.cdns
    ), "the ip for dns.google.com should be 8.8.8.8"


def test_all_checks_by_name():
    """Run all checks and get CDN name."""
    dom_in = Domain(
        "login.gov", list(), list(), list(), list(), list(), list(), list(), list()
    )
    check = cdnCheck()
    check.all_checks(dom_in)

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
        list(),
    )
    print(dom.url, dom.cdns, dom.cnames, dom.headers, dom.whois_data, dom.ip)
    check = cdnCheck()
    return_code = check.all_checks(dom)
    print(return_code)
    print(dom.url, dom.cdns, dom.cnames, dom.headers, dom.whois_data, dom.ip)
    assert return_code != 0, "This fake site should return a non 0 code."
