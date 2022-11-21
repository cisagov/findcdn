from typing import List
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
        self.errors = []
        self.cdn_present = False
