"""Whois analyzer for finding CDNs based on WHOIS records."""

# Standard Python Libraries
from re import match
from typing import List, Tuple

# Third-Party Libraries
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Timeout
from ipwhois import HTTPLookupError, IPDefinedError, IPWhois
from ipwhois.exceptions import ASNRegistryError, WhoisLookupError, WhoisRateLimitError

# cisagov Libraries
from findcdn.cdnEngine.analyzers.__cdn_config__ import CDNs

# Internal Libraries
from findcdn.cdnEngine.analyzers.base import BaseAnalyzer, Domain


class WHOISlyzer(BaseAnalyzer):
    """Perform whois lookup on domain."""

    __NAME = "WHOISlyzer"

    def get_data(self, domain: Domain) -> Tuple[List, int]:
        """Perform action to get data we need to detect a CDN."""
        whois_data = []
        error_code = 0

        try:
            for ip in domain.ips:
                while True:
                    try:
                        response = IPWhois(ip)
                        break
                    except WhoisRateLimitError:
                        pass

                # These two should be where we can find substrings hinting CDN
                org = response.lookup_whois().get("asn_description")
                if org and org != "BAREFRUIT-ERRORHANDLING":
                    whois_data.append(org)

                network = response.lookup_rdap().get("network")
                org = network.get("name") if network else None
                if org and org != "BAREFRUIT-ERRORHANDLING":
                    whois_data.append(org)
        except NoAnswer:
            error_code = 1
        except NoNameservers:
            error_code = 2
        except NXDOMAIN:
            error_code = 3
        except Timeout:
            error_code = 4
        except HTTPLookupError:
            error_code = 5
        except IPDefinedError:
            error_code = 6
        except ASNRegistryError:
            error_code = 7
        except WhoisLookupError:
            error_code = 8
        except Exception as e:
            print(f"[{e}]: {domain.domain} for {ip}")

        return whois_data, error_code

    def parse(self, whois_data: List) -> Tuple[List, int]:
        """Parse the data gathered and return CDN results."""
        cdns = []
        error_code = 0

        try:
            for data in whois_data:
                for cdn_regex, cdn_name in CDNs.items():
                    matches = match(cdn_regex, data.lower())
                    if matches:
                        res = matches.group()
                        if res:
                            cdns.append(cdn_name)
                    if cdn_name.lower() in data.lower():
                        cdns.append(cdn_name)
        except Exception as e:  # TODO fix exception usage
            print(e)
            error_code = 1

        return cdns, error_code
