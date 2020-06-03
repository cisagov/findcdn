"""detectCDN Library"""
from .cdn_check import cdnCheck, domain
from .cdn_config import API_URL, COMMON, CDNs, CDNs_rev
from .cdn_err import NoDomains, NoIPaddress

__all__ = [
    "domain",
    "cdnCheck",
    "CDNs_rev",
    "CDNs",
    "COMMON",
    "API_URL",
    "NoDomains",
    "NoIPaddress",
]
