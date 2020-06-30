#!/usr/bin/env python3

"""
Summary: This is the main runner for detectCDn.

Description: The detectCDN library is meant to show what CDNs a domain may be using
"""

# Standard Python Libraries
from http.client import RemoteDisconnected
from ssl import CertificateError, SSLError
from typing import List
from urllib.error import URLError
import urllib.request as request

# Third-Party Libraries
from ipwhois import HTTPLookupError, IPDefinedError, IPWhois
from ipwhois.exceptions import ASNRegistryError

# Internal Libraries
from .cdn_config import COMMON, CDNs, CDNs_rev
from .cdn_err import NoIPaddress

from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers  # isort:skip
from dns.resolver import Resolver, Timeout, query  # isort:skip

# Global variables
LIFETIME = 10


class Domain:
    """Domain class allows for storage of metadata on domain."""

    def __init__(
        self,
        url: str,
        ip: List[str] = [],
        cnames: List[str] = [],
        cdns: List[str] = [],
        cdns_by_name: List[str] = [],
        namsrvs: List[str] = [],
        headers: List[str] = [],
        whois_data: List[str] = [],
    ):
        """Initialize object to store metadata on domain in url."""
        self.url = url
        self.ip = ip
        self.cnames = cnames
        self.cdns = cdns
        self.cdns_by_name = cdns_by_name
        self.namesrvs = namsrvs
        self.headers = headers
        self.whois_data = whois_data
        self.cdn_present = False


class cdnCheck:
    """cdnCheck runs analysis and stores discovered data in Domain object."""

    def __init__(self):
        """Initialize the orchestrator of analysis."""
        self.running = False

    def ip(self, dom: Domain) -> List[int]:
        """Determine IP addresses the domain resolves to."""
        dom_list: List[str] = [dom.url, "www." + dom.url]
        return_codes = []
        ip_list = []
        for domain in dom_list:
            try:
                # Query the domain
                response = query(domain)
                # Assign any found IP addresses to the object
                for ip in response:
                    if str(ip.address) not in ip_list and str(ip.address) not in dom.ip:
                        ip_list.append(str(ip.address))
            except NoAnswer:
                return_codes.append(1)
            except NoNameservers:
                return_codes.append(2)
            except NXDOMAIN:
                return_codes.append(3)
            except Timeout:
                return_codes.append(4)

        # Append all addresses into IP_list
        for addr in ip_list:
            dom.ip.append(addr)
        # Return listing of error codes
        return return_codes

    def cname(self, dom: Domain, timeout: int) -> List[int]:
        """Collect CNAME records on domain."""
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
        return return_code

    def https_lookup(
        self, dom: Domain, timeout: int, agent: str, interactive: bool, verbose: bool
    ) -> int:
        """Read 'server' header for CDN hints."""
        # List of domains with different protocols to check.
        PROTOCOLS = ["https://", "https://www."]
        # Iterate through all protocols
        for PROTOCOL in PROTOCOLS:
            try:
                # Some domains only respond when we have a User-Agent defined.
                req = request.Request(
                    PROTOCOL + dom.url, data=None, headers={"User-Agent": agent},
                )
                # Making the timeout 50 as to not hang thread.
                response = request.urlopen(req, timeout=timeout)  # nosec
            except URLError:
                continue
            except RemoteDisconnected:
                continue
            except CertificateError:
                continue
            except ConnectionResetError:
                continue
            except SSLError:
                continue
            except Exception as e:
                # Define an exception just in case we missed one.
                if interactive or verbose:
                    print(f"[{e}]: https://{dom.url}")
                continue
            # Define headers to check for the response
            # to grab strings for later parsing.
            HEADERS = ["server", "via"]
            for value in HEADERS:
                if (
                    response.headers[value] is not None
                    and response.headers[value] not in dom.headers
                ):
                    dom.headers.append(response.headers[value])
        return 0

    def whois(self, dom: Domain, interactive: bool, verbose: bool) -> int:
        """Scrape WHOIS data for the org or asn_description."""
        # Make sure we have Ip addresses to check
        try:
            if len(dom.ip) <= 0:
                raise NoIPaddress
        except NoIPaddress:
            return 1
        # Define temp list to assign
        whois_data = []
        # Iterate through all the IP addresses in object
        for ip in dom.ip:
            try:
                response = IPWhois(ip)
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
            except HTTPLookupError:
                pass
            except IPDefinedError:
                pass
            except ASNRegistryError:
                pass
            except Exception as e:
                if interactive or verbose:
                    print(f"[{e}]: {dom.url} for {ip}")
        for data in whois_data:
            if data not in dom.whois_data:
                dom.whois_data.append(data)
        # Everything was successful
        return 0

    def CDNid(self, dom: Domain, data_blob: List):
        """
        Identify any CDN name in list received.

        All of these will be doing some sort of substring analysis
        on each string from any list passed to it. This will help
        us identify the CDN which could be used.
        """
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
            for name in COMMON.keys():
                if (
                    name.lower().replace(" ", "") in data.lower().replace(" ", "")
                    and CDNs_rev[name] not in dom.cdns
                ):
                    dom.cdns.append(CDNs_rev[name])
                    dom.cdns_by_name.append(name)

    def data_digest(self, dom: Domain) -> int:
        """Digest all data collected and assign to CDN list."""
        return_code = 1
        # Iterate through all attributes for substrings
        if len(dom.cnames) > 0 and not None:
            self.CDNid(dom, dom.cnames)
            return_code = 0
        if len(dom.headers) > 0 and not None:
            self.CDNid(dom, dom.headers)
            return_code = 0
        if len(dom.namesrvs) > 0 and not None:
            self.CDNid(dom, dom.namesrvs)
            return_code = 0
        if len(dom.whois_data) > 0 and not None:
            self.CDNid(dom, dom.whois_data)
            return_code = 0
        return return_code

    def all_checks(
        self,
        dom: Domain,
        timeout: int,
        agent: str,
        verbose: bool = False,
        interactive: bool = False,
    ) -> int:
        """Option to run everything in this library then digest."""
        # Obtain each attributes data
        self.ip(dom)
        self.cname(dom, timeout)
        self.https_lookup(dom, timeout, agent, interactive, verbose)
        self.whois(dom, interactive, verbose)

        # Digest the data
        return_code = self.data_digest(dom)

        # Extra case if we want verbosity for each domain check
        if verbose:
            if len(dom.cdns) > 0:
                print(f"{dom.url} has the following CDNs:\n{dom.cdns}")
            else:
                print(f"{dom.url} does not use a CDN")
        return return_code
