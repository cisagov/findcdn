#!/usr/bin/env python3

"""
Summary: This is the main runner for detectCDn.

Description: The detectCDN library is meant to show what CDNs a domain may be using
"""

# Standard Python Libraries
from http.client import RemoteDisconnected
import os
from typing import List
from urllib.error import URLError
import urllib.request as request

# Third-Party Libraries
import censys.websites as censysLookup
from ipwhois import HTTPLookupError, IPDefinedError, IPWhois

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
        censys_data: List[str] = [],
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
        self.censys_data = censys_data


class cdnCheck:
    """cdnCheck runs analysis and stores discovered data in Domain object."""

    def __init__(self):
        """Initialize the orchestrator of analysis. Grab Censys.io api keys from environment."""
        try:
            self.UID = os.environ["CENSYS_UID"]
        except KeyError:
            self.UID = None
        try:
            self.SECRET = os.environ["CENSYS_SECRET"]
        except KeyError:
            self.SECRET = None

    def ip(self, dom: Domain) -> int:
        """Determine IP addresses the domain resolves to."""
        try:
            response = query(dom.url)
            # Assign any found IP addresses
            dom.ip = [str(ip.address) for ip in response]
        except NXDOMAIN:
            return 1
        except NoNameservers:
            return 2
        except NoAnswer:
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
        except NXDOMAIN:
            return 2
        except Timeout:
            return 3
        except NoNameservers:
            return 4
        return 0

    def namesrv(self, dom: Domain) -> int:
        """Collect nameservers for potential cdn suggestions."""
        try:
            response = query(dom.url, "ns")
            dom.namesrvs = [server.to_text() for server in response]
        except NoAnswer:
            return 1
        except NXDOMAIN:
            return 2
        except NoNameservers:
            return 3
        return 0

    def https_lookup(self, dom: Domain):
        """Read 'server' header for CDN hints."""
        PROTOCOLS = ["https://"]
        for PROTOCOL in PROTOCOLS:
            try:
                response = request.urlopen(PROTOCOL + dom.url)  # nosec
                HEADERS = ["server", "via"]
                for value in HEADERS:
                    if response.headers[value] is not None:
                        dom.headers.append(response.headers[value])
            except URLError:
                pass
            except RemoteDisconnected:
                pass

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
        dom.whois_data = whois_data

    def censys(self, dom: Domain) -> int:
        """Query Censys API for information on domain."""
        if self.UID is None or self.SECRET is None:
            return 1
        # Data to return
        censys_data = []
        client = censysLookup.CensysWebsites(self.UID, self.SECRET)
        API_FIELDS = [
            "443.https.get.headers.server",
            "80.https.get.headers.server",
            "443.https.get.metadata.description",
            "443.https.get.headers.vary",
            "80.http.get.headers.vary",
            "80.http.get.metadata.description",
            "80.http_www.get.headers.unknown",
            "443.https.get.headers.unknown",
            "80.http_www.get.headers.server",
            "443.https.get.headers.via",
        ]
        data = list(client.search("domain: " + dom.url, API_FIELDS, max_records=10))

        # Make sure something valid returned
        if len(data) <= 0:
            return 2
        else:
            for value_set in data[0].values():
                if isinstance(value_set, list):
                    for discovered in value_set:
                        for info in discovered.values():
                            censys_data.append(info)
                else:
                    censys_data.append(value_set)
            dom.censys_data = censys_data
        return 0

    def CDNid(self, dom: Domain, data_blob: List):
        """Identify any CDN name in list recieved."""
        for data in data_blob:
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
        if len(dom.censys_data) > 0 and not None:
            self.CDNid(dom, dom.censys_data)
            return_code = 0
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

    def all_checks(self, dom: Domain):
        """Option to run everything in this library then digest."""
        self.ip(dom)
        self.cname(dom)
        self.namesrv(dom)
        self.https_lookup(dom)
        self.whois(dom)
        self.censys(dom)
        return self.data_digest(dom)
