#!/usr/bin/env pytest -vs
"""Tests for cdnEngine."""

# cisagov Libraries
import findcdn


def test_domainpot_init():
    """Test if DomainPot can be instantiated correctly."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    pot = findcdn.cdnEngine.DomainPot(domains)

    # Assertions
    for i in range(len(domains)):
        assert pot.domains[i].url == domains[i], "{} is not {}".format(
            pot.domains[i].url, domains[i]
        )
        for j in range(len(domains)):
            if j == i:
                continue
            assert id(pot.domains[i].cdns) != id(
                pot.domains[j].cdns
            ), "Domain obect {} shares address with Domain object {}".format(i, j)


def test_chef_init():
    """Test if Chef can be instantiated correctly."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    pot = findcdn.cdnEngine.DomainPot(domains)
    chef = findcdn.cdnEngine.Chef(pot)

    # Assertions
    assert type(chef.pot) == findcdn.cdnEngine.DomainPot


def test_grab_cdn():
    """Test if Chef can obtain proper CDNs of domains."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    pot = findcdn.cdnEngine.DomainPot(domains)
    chef = findcdn.cdnEngine.Chef(pot)
    chef.run_checks()
    checked_domains = chef.pot.domains

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
    pot = findcdn.cdnEngine.DomainPot(domains)
    chef = findcdn.cdnEngine.Chef(pot)
    chef.run_checks()
    checked_domains = chef.pot.domains

    # Assertions
    cdn_present = 0
    for dom in checked_domains:
        if dom.cdn_present:
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
    pot = findcdn.cdnEngine.DomainPot(domains)
    chef = findcdn.cdnEngine.Chef(pot)
    chef.run_checks()

    # Assertions
    assert len(chef.pot.domains) > 0, "Pot not stored correctly."


def test_run_checks_present():
    """Test the return of a list of cdn_present domains."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    objects, cnt, err = findcdn.cdnEngine.run_checks(domains)
    cdn_present = {}
    for dom in objects:
        if dom.cdn_present:
            cdn_present[dom.url] = dom.cdns
    expected = {
        "asu.edu": [".cloudflare.net", ".cloudflare.com"],
        "censys.io": [".cloudflare.com"],
        "adobe.com": [".edgekey.net", ".akamaitechnologies.fr"],
    }

    # Assertions
    assert len(cdn_present) > 0, "Returned cdn_present list is empty."
    assert cdn_present == expected, "Returned domains do not match."
