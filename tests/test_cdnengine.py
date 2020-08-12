#!/usr/bin/env pytest -vs
"""Tests for cdnengine."""

# Standard Python Libraries

# cisagov Libraries
import findcdn

# Test Global Variables
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
TIMEOUT = 30
THREADS = 0  # If 0 then cdnengine uses CPU count to set thread count


def test_chef_init():
    """Test if Chef can be instantiated correctly."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    chef = findcdn.cdnengine.Chef(domains, THREADS, TIMEOUT, USER_AGENT)

    # Assertions List[detectcdn.Domain]
    assert isinstance(chef.pot, list)


def test_grab_cdn():
    """Test if Chef can obtain proper CDNs of domains."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    chef = findcdn.cdnengine.Chef(domains, THREADS, TIMEOUT, USER_AGENT)
    chef.run_checks()
    checked_domains = chef.pot

    # Assertions
    assert checked_domains[0].cdns == [
        ".cloudflare.net",
        ".cloudflare.com",
    ], "Did not detect {} from {}.".format(
        [".cloudflare.net", ".cloudflare.com"], checked_domains[0].url
    )
    assert checked_domains[1].cdns == [
        ".cloudfront.net",
    ], "Did not detect {} from {}.".format([".cloudfront.net"], checked_domains[1].url)
    assert checked_domains[2].cdns == [
        ".cloudflare.com"
    ], "Did not detect {} from {}.".format([".cloudflare.com"], checked_domains[2].url)
    assert checked_domains[3].cdns == [
        ".cloudflare.com"
    ], "Did not detect {} from {}.".format([".cloudflare.com"], checked_domains[3].url)


def test_has_cdn():
    """Test that of a set of domains with a without a CDN return correctly."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    chef = findcdn.cdnengine.Chef(domains, THREADS, TIMEOUT, USER_AGENT)
    chef.run_checks()
    checked_domains = chef.pot

    # Assertions
    cdn_present = 0
    for dom in checked_domains:
        if len(dom.cdns) > 0:
            cdn_present += 1

    assert cdn_present == 3, "Too many cdn_present domains counted."
    assert checked_domains[0].url == "asu.edu" and checked_domains[0].cdns == [
        ".cloudflare.net",
        ".cloudflare.com",
    ], ("Incorrect CDN detected for %s" % checked_domains[0].url)
    assert checked_domains[1].url == "censys.io" and checked_domains[1].cdns == [
        ".cloudflare.com"
    ], ("Incorrect CDN detected for %s" % checked_domains[1].url)


def test_run_checks():
    """Test the run_checks orchestator works."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    chef = findcdn.cdnengine.Chef(domains, THREADS, TIMEOUT, USER_AGENT)
    chef.run_checks()

    # Assertions
    assert len(chef.pot) > 0, "Pot not stored correctly."


def test_run_checks_present():
    """Test the return of a list of cdn_present domains."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    objects, _ = findcdn.cdnengine.run_checks(domains, THREADS, TIMEOUT, USER_AGENT)
    cdn_present = {}
    for dom in objects:
        if len(dom.cdns) > 0:
            cdn_present[dom.url] = dom.cdns
    expected = {
        "asu.edu": [".cloudflare.net", ".cloudflare.com"],
        "censys.io": [".cloudflare.com"],
        "adobe.com": [".edgekey.net", ".akamaitechnologies.fr"],
    }

    # Assertions
    assert len(cdn_present) > 0, "Returned cdn_present list is empty."
    assert cdn_present == expected, "Returned domains do not match."
