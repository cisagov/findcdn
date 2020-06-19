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
        self.frontable = False


class cdnCheck:
    """cdnCheck runs analysis and stores discovered data in Domain object."""

    def __init__(self):
        """Initialize the orchestrator of analysis."""
        self.running = False

    def ip(self, dom: Domain) -> int:
        """Determine IP addresses the domain resolves to."""
        try:
            response = query(dom.url)
            # Assign any found IP addresses
            dom.ip = [str(ip.address) for ip in response]
        except NoAnswer:
            return 1
        except NoNameservers:
            return 2
        except NXDOMAIN:
            return 3
        except Timeout:
            return 4
        return 0

    def cname(self, dom: Domain) -> int:
        """Collect CNAME records on domain."""
        resolver = Resolver()
        resolver.timeout = 10
        resolver.lifetime = 10
        cname_query = resolver.query
        try:
            response = cname_query(dom.url, "cname")
            dom.cnames = [record.to_text() for record in response]
        except NoAnswer:
            return 1
        except NoNameservers:
            return 2
        except NXDOMAIN:
            return 3
        except Timeout:
            return 4
        return 0

    def https_lookup(self, dom: Domain):
        """Read 'server' header for CDN hints."""
        PROTOCOLS = ["https://"]
        for PROTOCOL in PROTOCOLS:
            try:
                req = request.Request(
                    PROTOCOL + dom.url,
                    data=None,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
                    },
                )
                # Making the timeout 50 as to not hang thread.
                response = request.urlopen(req, timeout=60)  # nosec
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
                print(f"[{e}]: {dom.url}")
                continue
            HEADERS = ["server", "via"]
            for value in HEADERS:
                if response.headers[value] is not None:
                    dom.headers.append(response.headers[value])
        return 0

    def whois(self, dom: Domain):
        """Scrape WHOIS data for the org or asn_description."""
        try:
            if len(dom.ip) <= 0:
                raise NoIPaddress
        except NoIPaddress:
            return 1
        # Define temp list to assign
        whois_data = []
        for ip in dom.ip:
            try:
                response = IPWhois(ip)
                org = response.lookup_rdap()["network"]["name"]
                if org != "BAREFRUIT-ERRORHANDLING":
                    whois_data.append(org)
            except HTTPLookupError:
                pass
            except IPDefinedError:
                pass
            except ASNRegistryError:
                pass
            except Exception as e:
                print(f"[{e}]: {dom.url}")
        dom.whois_data = whois_data

    def CDNid(self, dom: Domain, data_blob: List):
        """Identify any CDN name in list recieved."""
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

    def data_digest(self, dom: Domain):
        """Digest all data collected and assign to CDN list."""
        return_code = 1
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

    def all_checks(self, dom: Domain, verbose: bool = False):
        """Option to run everything in this library then digest."""
        self.ip(dom)
        self.cname(dom)
        self.https_lookup(dom)
        self.whois(dom)
        return_code = self.data_digest(dom)
        if verbose:
            if len(dom.cdns) > 0:
                print(f"{dom.url} has the following CDNs:\n{dom.cdns}")
            else:
                print(f"{dom.url} does not use a CDN")
        return return_code
