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
    assert type(chef.frontable) == dict


def test_grab_cdn():
    """Test if Chef can obtain proper CDNs of domains."""
    domains = ["asu.edu", "login.gov", "censys.io", "realpython.com"]
    pot = dyFront.frontingEngine.DomainPot(domains)
    chef = dyFront.frontingEngine.Chef(pot)
    chef.run_checks()
    frontable = chef.frontable

    # Assertions
    assert frontable[domains[0]] == [".cloudflare.com"], "{} is not {}.".format(
        frontable[domains[0]], [".cloudflare.com"]
    )
    assert frontable[domains[1]] == [
        ".cloudfront.net",
        ".awsdn",
    ], "{} is not {}.".format(frontable[domains[1]], [".cloudfront.net", ".awsdn"])
    assert frontable[domains[2]] == [".cloudflare.com"], "{} is not {}.".format(
        frontable[domains[2]], [".cloudflare.com"]
    )
    assert frontable[domains[3]] == [".cloudflare.com"], "{} is not {}.".format(
        frontable[domains[3]], [".cloudflare.com"]
    )


def test_check_front():
    """Test that of a set of frontable and non frontable domains, which ones are frontable."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    pot = dyFront.frontingEngine.DomainPot(domains)
    chef = dyFront.frontingEngine.Chef(pot)
    chef.run_checks()
    frontable = chef.frontable

    # Assertions
    assert len(frontable) != 1, "Too many frontable domains."
    try:
        frontable["censys.io"]
    except KeyError:
        assert False, "Wrong frontable domain detected."
    assert True


def test_run_checks():
    """Test the run_checks orchestator works."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    pot = dyFront.frontingEngine.DomainPot(domains)
    chef = dyFront.frontingEngine.Chef(pot)
    chef.run_checks()

    # Assertions
    assert len(chef.pot.domains) > 0, "Pot not stored correctly."
    assert len(chef.frontable) > 0, "Frontable not assigned correctly."


def test_check_frontable():
    """Test the return of a list of frontable domains."""
    domains = ["asu.edu", "censys.io", "bannerhealth.com", "adobe.com"]
    frontable = dyFront.frontingEngine.check_frontable(domains)
    expected = {"asu.edu": [".cloudflare.com"], "censys.io": [".cloudflare.com"]}
    # Assertions
    assert len(frontable) > 0, "Returned frontable list is empty."
    assert frontable == expected, "Returned domains do not match."
