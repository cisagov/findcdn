#!/usr/bin/env pytest -vs
"""Tests for detectCDN."""

import os
import sys
# from unittest.mock import patch

# Third-Party Libraries
import pytest

# cisagov Libraries

from dyFront.frontingEngine.detectCDN import cdnCheck, Domain


def test_ip():
    """Test the IP resolving feature"""
    dom_in = Domain("dns.google.com")
    check = cdnCheck()
    check.ip(dom_in)

    assert "8.8.8.8" in dom_in.ip, "the ip for dns.google.com should be 8.8.8.8"

    """ ToDo this part.
    def test_broken_ip():
        Working domain list to test with.
        dom_in = Domain("dns.gooasdfasdfasdfasdfasdfasdfasdfasdfasdfasfasdfgle.com")
        check = cdnCheck()
        check.ip(dom_in)

        assert "8.8.8.8" in dom_in.ip, "the ip for dns.google.com should be 8.8.8.8"
    """


def test_cname():
    """Test the CNAME resolving feature."""
    dom_in = Domain("www.asu.edu")
    check = cdnCheck()
    check.cname(dom_in)

    assert "www.asu.edu.cdn.cloudflare.net." in dom_in.cnames, "www.asu.edu should have www.asu.edu.cdn.cloudflare.net. as a cname"


def test_namesrv():
    """Test the namesrv resolving feature."""
    dom_in = Domain("google.com")
    check = cdnCheck()
    check.namesrv(dom_in)

    assert "ns1.google.com." in dom_in.namesrvs, "google.com should have ns1.google.com. as a nameserver"


def test_https_lookup():
    """Test the header resolving feature."""
    dom_in = Domain("google.com")
    check = cdnCheck()
    check.https_lookup(dom_in)

    assert "gws" in dom_in.headers, "google.com should have gws as a header"


def test_whois():
    """Test the whois resolving feature."""
    dom_in = Domain("google.com")
    check = cdnCheck()
    check.ip(dom_in)
    check.whois(dom_in)

    assert "GOOGLE" in dom_in.whois_data, "google.com should return GOOGLE in the whois_data"


# def test_whois_no_ip():
#     """Working domain list to test with."""
#     dom_in = Domain("google.com")
#     check = cdnCheck()
#     check.whois(dom_in)

#     assert "gws" in dom_in.whois_data, "the ip for dns.google.com should be 8.8.8.8"

# def test_censys():
#     """Working domain list to test with."""
#     dom_in = Domain("google.com")
#     check = cdnCheck()
#     check.cname(dom_in)
#     assert "8.8.8.8" in dom_in.cnames, "the ip for dns.google.com should be 8.8.8.8"


# def test_data_digest():
#     """Working domain list to test with."""
#     dom_in = Domain("google.com")
#     check = cdnCheck()
#     check.cname(dom_in)

#     assert "8.8.8.8" in dom_in.cnames, "the ip for dns.google.com should be 8.8.8.8"

# def test_all_checks():
#     """Working domain list to test with."""
#     dom_in = Domain("google.com")
#     check = cdnCheck()
#     check.cname(dom_in)

#     assert "8.8.8.8" in dom_in.cnames, "the ip for dns.google.com should be 8.8.8.8"
        