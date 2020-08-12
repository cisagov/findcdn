#!/usr/bin/env python3

"""
Summary: This is the main runner for detectCDn.

Description: The detectCDN library is meant to show what CDNs a domain may be using
"""

# Standard Python Libraries
from http.client import HTTPException, RemoteDisconnected
import socket
from ssl import CertificateError, SSLError
from typing import List
from urllib import request
from urllib.error import HTTPError, URLError

# Third-Party Libraries
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Resolver, Timeout, query
from ipwhois import HTTPLookupError, IPDefinedError, IPWhois
from ipwhois.exceptions import ASNRegistryError


# Internal Libraries
from .cdn_config import COMMON, CDNs, CDNs_rev
from .cdn_err import NoIPaddress

# Global variables
LIFETIME = 10


class Domain:
    """Domain class allows for storage of metadata on domain."""

    # pylint: disable=too-many-instance-attributes
    # 9 is the amount of attributes we need this object to have
    # pylint: disable=too-few-public-methods
    # This class doesnt need methods since we can call .<attribute> on the object.

    def __init__(
        self, url: str,
    ):
        """Initialize object to store metadata on domain in url."""
        self.url = url
        self.ip_list: List[str] = list()
        self.cnames: List[str] = list()
        self.cdns: List[str] = list()
        self.cdns_by_name: List[str] = list()
        self.headers: List[str] = list()
        self.whois_data: List[str] = list()


def ip_resolve(dom: Domain) -> List[int]:
    """Determine IP addresses the domain resolves to."""
    # Check if we have initialized the ip list
    if dom.ip_list is None:
        dom.ip_list = list()
    # Define our list of variant urls
    dom_list: List[str] = [dom.url, "www." + dom.url]
    # Lists to contain data from runs
    return_codes = []
    ip_list = []
    # Iterate over domains for the ip addresses
    for domain in dom_list:
        try:
            # Query the domain
            response = query(domain)
            # Assign any found IP addresses to the object
            for ip_iter in response:
                if (
                    str(ip_iter.address) not in ip_list
                    and str(ip_iter.address) not in dom.ip_list
                ):
                    ip_list.append(str(ip_iter.address))
        except NoAnswer:
            return_codes.append(1)
        except NoNameservers:
            return_codes.append(2)
        except NXDOMAIN:
            return_codes.append(3)
        except Timeout:
            return_codes.append(4)
        except (socket.timeout, URLError, HTTPError):
            pass

    # Append all addresses into IP_list
    for addr in ip_list:
        dom.ip_list.append(addr)
    # Return listing of error codes
    return return_codes


def cname(dom: Domain, timeout: int) -> List[int]:
    """Collect CNAME records on domain."""
    # Make sure we initialized the cname list
    if dom.cnames is None:
        dom.cnames = list()
    # List of domains to check
    dom_list = [dom.url, "www." + dom.url]
    # Our codes to return
    return_code = []
    # Seutp resolver and timeouts
    resolver = Resolver()
    resolver.timeout = timeout
    resolver.lifetime = LIFETIME
    cname_query = resolver.query
    # Iterate through all domains in list
    for domain in dom_list:
        try:
            response = cname_query(domain, "cname")
            dom.cnames = [record.to_text() for record in response]
        except NoAnswer:
            return_code.append(1)
        except NoNameservers:
            return_code.append(2)
        except NXDOMAIN:
            return_code.append(3)
        except Timeout:
            return_code.append(4)
        except (socket.timeout, URLError, HTTPError):
            pass
    return return_code


def https_lookup(dom: Domain, timeout: int, agent: str) -> int:
    """Read 'server' header for CDN hints."""
    # Check if we have initialized the headers list
    if dom.headers is None:
        dom.headers = list()
    # List of domains with different protocols to check.
    protocols = ["https://", "https://www."]
    # Iterate through all protocols
    for protocol in protocols:
        try:
            # Some domains only respond when we have a User-Agent defined.
            req = request.Request(
                protocol + dom.url, data=None, headers={"User-Agent": agent},
            )
            # The use of urlopen is safe in this context as we do not let the user
            # have choice over the use of what protocol urlopen() uses. 
            response = request.urlopen(req, timeout=timeout)  # nosec
        except (
            HTTPError,
            URLError,
            RemoteDisconnected,
            CertificateError,
            ConnectionResetError,
            SSLError,
            Timeout,
            socket.timeout,
            socket.error,
            HTTPException,
        ):
            continue
        # Define headers to check for the response
        # to grab strings for later parsing.
        headers = ["server", "via"]
        for value in headers:
            if (
                response.headers[value] is not None
                and response.headers[value] not in dom.headers
            ):
                dom.headers.append(response.headers[value])
    return 0


def whois(dom: Domain) -> int:
    """Scrape WHOIS data for the org or asn_description."""
    # pylint: disable=too-many-branches

    # Unfortunately, need all of these branches to catch specific
    # errors as not all servers respond the same

    # Make sure we have Ip addresses to check
    try:
        if dom.ip_list is None or len(dom.ip_list) <= 0:
            raise NoIPaddress
    except NoIPaddress:
        return 1
    # Make sure our domain object has initialized whois data list
    if dom.whois_data is None:
        dom.whois_data = list()
    # Define temp list to assign
    whois_data = []
    # Iterate through all the IP addresses in object
    for ip_val in dom.ip_list:
        try:
            response = IPWhois(ip_val)
            # These two should be where we can find substrings hinting to CDN
            try:
                org = response.lookup_whois()["asn_description"]
                if org != "BAREFRUIT-ERRORHANDLING":
                    whois_data.append(org)
            except AttributeError:
                pass
            try:
                org = response.lookup_rdap()["network"]["name"]
                if org != "BAREFRUIT-ERRORHANDLING":
                    whois_data.append(org)
            except AttributeError:
                pass
        except (
            HTTPLookupError,
            HTTPError,
            URLError,
            IPDefinedError,
            ASNRegistryError,
            Timeout,
            socket.timeout,
        ):
            pass

    for data in whois_data:
        if data not in dom.whois_data:
            dom.whois_data.append(data)
    # Everything was successful
    return 0


def cdn_id(dom: Domain, data_blob: List):
    """
    Identify any CDN name in list received.

    All of these will be doing some sort of substring analysis
    on each string from any list passed to it. This will help
    us identify the CDN which could be used.
    """
    # Check if our cdn list is initialized
    if dom.cdns_by_name is None or dom.cdns is None:
        dom.cdns = list()
        dom.cdns_by_name = list()

    # Iterate over all the data sent in
    for data in data_blob:
        # Make sure we do not try to analyze None type data
        if data is None:
            continue
        # Check the CDNs standard list
        for url in CDNs:
            if (
                url.lower().replace(" ", "") in data.lower().replace(" ", "")
                and url not in dom.cdns
            ):
                dom.cdns.append(url)
                dom.cdns_by_name.append(CDNs[url])

        # Check the CDNs reverse list
        for name in CDNs_rev:
            if name.lower() in data.lower() and CDNs_rev[name] not in dom.cdns:
                dom.cdns.append(CDNs_rev[name])
                dom.cdns_by_name.append(name)

        # Check the CDNs Common list:
        for name in COMMON:
            if (
                name.lower().replace(" ", "") in data.lower().replace(" ", "")
                and CDNs_rev[name] not in dom.cdns
            ):
                dom.cdns.append(CDNs_rev[name])
                dom.cdns_by_name.append(name)


def data_digest(dom: Domain) -> int:
    """Digest all data collected and assign to CDN list."""
    return_code = 1
    # Iterate through all attributes for substrings
    if len(dom.cnames) > 0 and not None:
        cdn_id(dom, dom.cnames)
        return_code = 0
    if len(dom.headers) > 0 and not None:
        cdn_id(dom, dom.headers)
        return_code = 0
    if len(dom.whois_data) > 0 and not None:
        cdn_id(dom, dom.whois_data)
        return_code = 0
    return return_code


def all_checks(dom: Domain, timeout: int, agent: str, verbose: bool = False,) -> int:
    """Option to run everything in this library then digest."""
    # Obtain each attributes data
    ip_resolve(dom)
    cname(dom, timeout)
    https_lookup(dom, timeout, agent)
    whois(dom)

    # Digest the data
    return_code = data_digest(dom)

    # Extra case if we want verbosity for each domain check
    if verbose:
        if len(dom.cdns) > 0:
            print(f"{dom.url} has the following CDNs:\n{dom.cdns}")
        else:
            print(f"{dom.url} does not use a CDN")

    # Return to calling function
    return return_code
