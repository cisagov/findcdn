#!/usr/bin/env python3

"""
The detectCDN library is meant to give functionality for
detecting the CDN a website/target domain may be using.
"""

# Standard Python Libraries 
import os
from typing import List

# Third-Party Libraries
import urllib.request as request
import censys.websites as censysLookup
from urllib.error import HTTPError, URLError
from dns.resolver import query, NoAnswer, NXDOMAIN, NoNameservers
from ipwhois import IPWhois

# Internal Libraries
from .cdn_config import *
from .cdn_err import *

class domain:
    def __init__(self, url: str,
                 ip: List[str]=[],
                 cnames: List[str]=[],
                 cdns: List[str]=[],
                 cdns_by_name: List[str]=[],
                 namsrvs: List[str]=[],
                 headers: List[str]=[],
                 whois_data: List[str]=[],
                 censys_data: List[str]=[]):
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
    def __init__(self):
        try:
            self.UID = os.environ["CENSYS_UID"]
        except KeyError as e:
            self.UID = None
        try:
            self.SECRET = os.environ["CENSYS_SECRET"]
        except KeyError as e:
            self.SECRET = None

    """
    Determine IP addresses the domain resolves to.
    """
    def ip(self, dom: domain):
        # Attempt to query the domain
        try:
            response = query(dom.url)
            # Assign any found IP addresses
            dom.ip = [str(ip.address) for ip in response]
        except NXDOMAIN:
            pass
        except NoNameservers:
            pass
        except NoAnswer:
            pass


    """
    Collect CNAME records on domain
    """
    def cname(self, dom: domain):
        # Attempt to query the domain for CNAME
        try:
            response = query(dom.url,'cname')
            dom.cnames = [record.to_text() for record in response]
        except NoAnswer as err:
            pass
        except NXDOMAIN:
            pass

    """
    Collect nameservers for potential cdn suggestions
    """
    def namesrv(self, dom: domain):
        # Check for any nameservers 
        try:
            response = query(dom.url, 'ns')
            dom.namesrvs = [server.to_text() for server in response]
        except NoAnswer:
            pass
        except NXDOMAIN:
            pass

    """
    Read 'server' header for CDN hints.
    """
    def https_lookup(self, dom: domain):
        # Request from webserver, read ['server']
        PROTOCOL = "http"
        try:
            response = request.urlopen(PROTOCOL + "://" + dom.url)
            dom.headers = response.headers["server"]
        except:
            pass

    """
    Scrape WHOIS data for the org or asn_description.
    """
    def whois(self, dom: domain):
        if len(dom.ip) <= 0:
            raise NoIPaddress
        # Define temp list to assign
        whois_data = []
        for ip in dom.ip:
            response = IPWhois(ip)
            org = response.lookup_rdap()['network']['name']
            whois_data.append(org)
        dom.whois_data = whois_data

    """
    Querying Censys API for information on domain
    """
    def censys(self, dom: domain):
        if self.UID is None or self.SECRET is None:
            return -1
        # Data to return
        censys_data = []
        client = censysLookup.CensysWebsites(self.UID,self.SECRET)
        API_FIELDS = ['443.https.get.headers.server',
                      '80.https.get.headers.server',
                      '443.https.get.metadata.description',
                      '443.https.get.headers.vary',
                      '80.http.get.headers.vary',
                      '80.http.get.metadata.description',
                      '80.http_www.get.headers.unknown',
                      '443.https.get.headers.unknown',
                      '80.http_www.get.headers.server',
                      '443.https.get.headers.via']
        data = list(client.search("domain: " + self.dom,
                             API_FIELDS, max_records=10))
        for value_set in data[0].values():
            if isinstance(url,list):
                for discovered in value_set:
                    for info in discovered.values():
                        censys_data.append(info)
            else:
                censys_data.append(value_set)
        dom.censys_data = censys_data

    """
    Identify any CDN name in list recieved
    """
    def CDNid(self, dom: domain, data_blob: List):
        for data in data_blob:
            # Check the CDNs standard list
            for url in CDNs:
                if url.lower().replace(
                        " ", "") in data.lower().replace(
                        " ", "") and url not in dom.cdns:
                    dom.cdns.append(url)
                    dom.cdns_by_name.append(CDNs[url])

            # Check the CDNs reverse list
            for name in CDNs_rev:
                if name.lower().replace(
                        " ", "") in data.lower().replace(
                        " ", "") and CDNs_rev[name] not in dom.cdns:
                    dom.cdns.append(CDNs_rev[name])
                    dom.cdns_by_name.append(name)

            # Check the CDNs Common list:
            for name in COMMON.keys():
                if name.lower().replace(
                        " ", "") in data.lower().replace(
                        " ", "") and CDNs_rev[name] not in dom.cdns:
                    dom.cdns.append(CDNs_rev[name])
                    dom.cdns_by_name.append(name)
    """
    Digest all data collected and assign to CDN list
    """
    def data_digest(self, dom: domain):
        # Digest all local lists of data
        if len(dom.censys_data) > 0 and not None:
            self.CDNid(dom, dom.censys_data)
        if len(dom.cnames) > 0 and not None:
            self.CDNid(dom, dom.cnames)
        if len(dom.headers) > 0 and not None:
            self.CDNid(dom, dom.headers)
        if len(dom.namesrvs) > 0 and not None:
            self.CDNid(dom, dom.namesrvs)
        if len(dom.whois_data) > 0 and not None:
            self.CDNid(dom, dom.whois_data)

    """
    An option to run everything in this library then digest.
    """
    def all_checks(self, dom: domain):
        self.ip(dom)
        self.cname(dom)
        self.namesrv(dom)
        self.https_lookup(dom)
        self.whois(dom)
        self.censys(dom)
        self.data_digest(dom)



























