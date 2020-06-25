"""detectCDN Library."""
from .cdn_check import Domain, cdnCheck
from .cdn_config import COMMON, CDNs, CDNs_rev
from .cdn_err import NoIPaddress

__all__ = [
    "Domain",
    "cdnCheck",
    "CDNs_rev",
    "CDNs",
    "COMMON",
    "NoIPaddress",
]
