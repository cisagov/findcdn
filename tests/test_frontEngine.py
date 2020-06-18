#!/usr/bin/env pytest -vs
"""Tests for frontingEngine."""

# cisagov Libraries
import dyFront


def test_domainpot_init():
    """Test if DomainPot can be instantiated correctly."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    pot = dyFront.frontingEngine.DomainPot(domains)

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
    pot = dyFront.frontingEngine.DomainPot(domains)
    chef = dyFront.frontingEngine.Chef(pot)

    # Assertions
    assert type(chef.pot) == dyFront.frontingEngine.DomainPot


def test_grab_cdn():
    """Test if Chef can obtain proper CDNs of domains."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    pot = dyFront.frontingEngine.DomainPot(domains)
    chef = dyFront.frontingEngine.Chef(pot)
    chef.run_checks()
    checked_domains = chef.pot.domains

    # Assertions
    assert checked_domains[0].cdns == [
        ".cloudflare.com"
    ], "Did not detect {} from {}.".format([".cloudflare.com"], checked_domains[0].url)
    assert checked_domains[1].cdns == [
        ".cloudfront.net",
    ], "Did not detect {} from {}.".format([".cloudfront.net"], checked_domains[1].url)
    assert checked_domains[2].cdns == [
        ".cloudflare.com"
    ], "Did not detect {} from {}.".format([".cloudflare.com"], checked_domains[2].url)
    assert checked_domains[3].cdns == [
        ".cloudflare.com"
    ], "Did not detect {} from {}.".format([".cloudflare.com"], checked_domains[3].url)


def test_check_front():
    """Test that of a set of frontable and non frontable domains, which ones are frontable."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    pot = dyFront.frontingEngine.DomainPot(domains)
    chef = dyFront.frontingEngine.Chef(pot)
    chef.run_checks()
    checked_domains = chef.pot.domains

    # Assertions
    frontable = 0
    for dom in checked_domains:
        if dom.frontable:
            frontable += 1

    assert frontable == 2, "Too many frontable domains counted."
    assert checked_domains[0].url == "asu.edu" and checked_domains[0].cdns == [
        ".cloudflare.com"
    ], ("Incorrect CDN detected for %s" % checked_domains[0].url)
    assert checked_domains[1].url == "censys.io" and checked_domains[1].cdns == [
        ".cloudflare.com"
    ], ("Incorrect CDN detected for %s" % checked_domains[1].url)


def test_run_checks():
    """Test the run_checks orchestator works."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    pot = dyFront.frontingEngine.DomainPot(domains)
    chef = dyFront.frontingEngine.Chef(pot)
    chef.run_checks()

    # Assertions
    assert len(chef.pot.domains) > 0, "Pot not stored correctly."


def test_check_frontable():
    """Test the return of a list of frontable domains."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    objects = dyFront.frontingEngine.check_frontable(domains)
    frontable = {}
    for dom in objects:
        if dom.frontable:
            frontable[dom.url] = dom.cdns
    expected = {"asu.edu": [".cloudflare.com"], "censys.io": [".cloudflare.com"]}
    # Assertions
    assert len(frontable) > 0, "Returned frontable list is empty."
    assert frontable == expected, "Returned domains do not match."
