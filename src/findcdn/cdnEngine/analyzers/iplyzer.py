"""IP Analyzer module for identifying CDNs through IP blocks."""

# Standard Python Libraries
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import List, Tuple, Union

# Third-Party Libraries
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Resolver, Timeout

# cisagov Libraries
from findcdn.cdnEngine.analyzers.__cdn_config__ import CDN_RANGES

# Internal Libraries
from findcdn.cdnEngine.analyzers.base import BaseAnalyzer, Domain


class IPlyzer(BaseAnalyzer):
    """Obtain IP address of domain and check."""

    __NAME = "IPlyzer"
    lifetime: int = 10

    def get_data(self, domain: Domain) -> Tuple[List, int]:
        """Perform action to get data we need to detect a CDN."""
        ip_list: List[Union[str, IPv4Address, IPv6Address]] = []
        error_code = 0

        if len(domain.ips) > 0:
            return domain.ips, 0

        resolver = Resolver()
        resolver.timeout = self.timeout
        resolver.lifetime = self.lifetime

        try:
            for ip in resolver.resolve(domain.domain):
                addr = ip_address(str(ip))
                if addr not in ip_list:
                    ip_list.append(addr)
        except NoAnswer:
            error_code = 1
        except NoNameservers:
            error_code = 2
        except NXDOMAIN:
            error_code = 3
        except Timeout:
            error_code = -1

        domain.ips = ip_list

        return ip_list, error_code

    def parse(self, ips: List) -> Tuple[List, int]:
        """Parse the data gathered and return CDN results."""
        cdns = []
        error_code = 0

        try:
            for cdn, iprange in CDN_RANGES.items():
                for ipaddr in ips:
                    for block in iprange:
                        if ip_address(ipaddr) in block:
                            cdns.append((ipaddr, cdn))
        except Exception as e:
            print(e)
            error_code = 1

        return [res[1] for res in cdns], error_code
