"""CNAME analyzer to identify CDNs from CNAME records."""

# Standard Python Libraries
from re import match
from typing import List, Tuple

# Third-Party Libraries
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Resolver, Timeout

# cisagov Libraries
from findcdn.cdnEngine.analyzers.__cdn_config__ import CDNs

# Internal Libraries
from findcdn.cdnEngine.analyzers.base import BaseAnalyzer, Domain


class CNAMElyzer(BaseAnalyzer):
    """Perform CNAME lookup based on domain."""

    __NAME = "CNAMElyzer"
    lifetime = 10

    def get_data(self, domain: Domain) -> Tuple[List, int]:
        """Get CNAME Records Of Domain."""
        cnames = []
        error_code = 0
        # Setup manual Resolver
        resolver = Resolver()
        resolver.timeout = self.timeout
        resolver.lifetime = self.lifetime

        try:
            resp = resolver.resolve(domain.domain, "cname")
            cnames = [record.to_text() for record in resp]
        except NoAnswer:
            error_code = 1
        except NoNameservers:
            error_code = 2
        except NXDOMAIN:
            error_code = 3
        except Timeout:
            error_code = 4

        return cnames, error_code

    def parse(self, cnames: List) -> Tuple[List, int]:
        """Parse the data gathered and return CDN results."""
        cdns = []
        error_code = 0

        try:
            for record in cnames:
                for cdn_regex, cdn_name in CDNs.items():
                    matches = match(cdn_regex, record.lower())
                    if matches:
                        res = matches.group()
                        if res:
                            cdns.append(cdn_name)

        except Exception as e:  # TODO fix exception usage
            print(e)
            error_code = 1

        return cdns, error_code
