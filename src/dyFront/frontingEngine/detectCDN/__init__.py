"""detectCDN Library"""
from .cdn_check import domain, cdnCheck
from .cdn_config import CDNs_rev, CDNs, COMMON, API_URL
from .cdn_err import NoDomains, NoIPaddress

__all__ = ["domain",
           "cdnCheck",
           "CDNs_rev",
           "CDNs",
           "COMMON",
           "API_URL",
           "NoDomains",
           "NoIPaddress"]
