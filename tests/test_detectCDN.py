#!/usr/bin/env pytest -vs
"""Tests for detectCDN."""

# cisagov Libraries
from dyFront.frontingEngine.detectCDN import Domain, cdnCheck

# from unittest.mock import patch


def test_ip():
    """Test the IP resolving feature."""
    dom_in = Domain("dns.google.com")
    check = cdnCheck()
    check.ip(dom_in)

    assert "8.8.8.8" in dom_in.ip, "the ip for dns.google.com should be 8.8.8.8"


def test_broken_ip():
    """Test a non-working domain IP resolving feature."""
    dom_in = Domain("notarealdomain.fakedomaindne.com")
    check = cdnCheck()
    return_code = check.ip(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_cname():
    """Test the CNAME resolving feature."""
    dom_in = Domain("www.asu.edu")
    check = cdnCheck()
    check.cname(dom_in)

    assert (
        "www.asu.edu.cdn.cloudflare.net." in dom_in.cnames
    ), "www.asu.edu should have www.asu.edu.cdn.cloudflare.net. as a cname"


def test_broken_cname():
    """Test a non-working domain CNAME resolving feature."""
    dom_in = Domain("notarealdomain.fakedomaindne.com")
    check = cdnCheck()
    return_code = check.cname(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_namesrv():
    """Test the namesrv resolving feature."""
    dom_in = Domain("google.com")
    check = cdnCheck()
    check.namesrv(dom_in)

    assert (
        "ns1.google.com." in dom_in.namesrvs
    ), "google.com should have ns1.google.com. as a nameserver"


def test_broken_namesrv():
    """Test a non-working domain namesrv resolving feature."""
    dom_in = Domain("notarealdomain.fakedomaindne.com")
    check = cdnCheck()
    return_code = check.namesrv(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_https_lookup():
    """Test the header resolving feature."""
    dom_in = Domain("google.com")
    check = cdnCheck()
    check.https_lookup(dom_in)

    assert "gws" in dom_in.headers, "google.com should have gws as a header"


def test_broken_https_lookup():
    """Test a non-working domain header resolving feature."""
    dom_in = Domain("notarealdomain.fakedomaindne.com")
    check = cdnCheck()
    return_code = check.namesrv(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."


def test_whois():
    """Test the whois resolving feature."""
    dom_in = Domain("google.com")
    check = cdnCheck()
    check.ip(dom_in)
    check.whois(dom_in)

    assert (
        "GOOGLE" in dom_in.whois_data
    ), "google.com should return GOOGLE in the whois_data"


def test_broken_whois():
    """Test a non-working domain whois resolving feature."""
    dom_in = Domain("notarealdomain.fakedomaindne.com")
    check = cdnCheck()
    check.ip(dom_in)
    return_code = check.whois(dom_in)
    assert return_code != 0, "This fake site should return a non 0 code."

# TODO: make test for this function
# def test_censys():
#     """Working domain list to test with."""
#     dom_in = Domain("google.com")
#     check = cdnCheck()
#     check.cname(dom_in)
#     assert "8.8.8.8" in dom_in.cnames, "the ip for dns.google.com should be 8.8.8.8"


def test_all_checks():
    """Working domain list to test with."""
    dom_in = Domain("login.gov")
    check = cdnCheck()
    check.all_checks(dom_in)

    assert ".cloudfront.net" in dom_in.cdns, "the ip for dns.google.com should be 8.8.8.8"


def test_all_checks_by_name():
    """Working domain list to test with."""
    dom_in = Domain("login.gov")
    check = cdnCheck()
    check.all_checks(dom_in)

    assert "Cloudfront" in dom_in.cdns_by_name, "the ip for dns.google.com should be 8.8.8.8"


def test_all_checks_bad():
    """Working domain list to test with."""
    dom_in = Domain("notarealdomain.fakedomaindne.com")
    check = cdnCheck()
    return_code = check.all_checks(dom_in)
    print(return_code)
    assert return_code != 0, "This fake site should return a non 0 code."
