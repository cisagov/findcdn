"""detectCDN Library."""
from .cdn_check import Domain, all_checks, cname, https_lookup, ip_resolve, whois
from .cdn_config import COMMON, CDNs, CDNs_rev
from .cdn_err import NoIPaddress

__all__ = [
    "Domain",
    "all_checks",
    "ip_resolve",
    "cname",
    "https_lookup",
    "whois",
    "CDNs_rev",
    "CDNs",
    "COMMON",
    "NoIPaddress",
]
