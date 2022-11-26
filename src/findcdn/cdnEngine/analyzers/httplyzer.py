"""HTTP Analyzer module for finding cdn based on HTTP headers."""

# Standard Python Libraries
from re import search
from typing import List, Tuple

# Third-Party Libraries
from requests import ConnectionError, ConnectTimeout, ReadTimeout, get

# cisagov Libraries
from findcdn.cdnEngine.analyzers.__cdn_config__ import CDNs

# Internal Libraries
from findcdn.cdnEngine.analyzers.base import BaseAnalyzer, Domain


class HTTPlyzer(BaseAnalyzer):
    """Reach out to host. Get headers."""

    __NAME = "IPlyzer"

    def get_data(self, domain: Domain) -> Tuple[List, int]:
        """Perform action to get data we need to detect a CDN."""
        http_data = []
        error_code = 0

        PROTOCOLS = ["http://", "https://"]
        INTERESTING_HEADERS = [
            "server",
            "via",
            "x-cache",
            "cf-cache-status",  # This is specific to cloudflare
        ]
        AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36"

        # Verify if we have had good hosts yet
        if len(domain.ips) != 0:
            # Get request with the intent a redirection will happen
            for proto in PROTOCOLS:
                try:
                    response = get(
                        f"{proto}{domain.domain}",
                        allow_redirects=True,
                        headers={"User-Agent": AGENT},
                        timeout=self.timeout,
                    )

                    # Validate all redirects (if any) are from the same domain
                    valid = True
                    for resp in response.history:
                        dom = search("https?://([A-Za-z_0-9.-]+).*", resp.url)
                        if dom:
                            valid &= all(
                                [i == domain.domain for i in list(dom.groups())]
                            )

                    if not valid:
                        error_code = 1
                    else:
                        # Collect headers
                        headers = []
                        for resp in response.history:
                            headers.append(resp.headers)
                        headers.append(response.headers)

                        # Iterate over them collecting data
                        for header in headers:
                            for h in INTERESTING_HEADERS:
                                http_data.append(header.get(h))

                        # Find out if we are using some sort of cache
                        for header in headers:
                            for h, v in dict(header).items():
                                if "-cache" in h.lower() and "drupal" not in h.lower():
                                    http_data.append("CDN_NOT_RECOGNIZED")
                except ConnectTimeout:
                    error_code |= 1
                except ConnectionError:
                    error_code |= 2
                except ReadTimeout:
                    error_code |= 3

        return http_data, error_code

    def parse(self, http_data: List) -> Tuple[List, int]:
        """Parse the data gathered and return CDN results."""
        cdns = []
        error_code = 0

        try:
            for data in http_data:
                if data:
                    for cdn_regex, cdn_name in CDNs.items():
                        matches = search(cdn_regex, data.lower())
                        if matches:
                            res = matches.group()
                            if res:
                                cdns.append(cdn_name)
                        if cdn_name.lower() in data.lower():
                            cdns.append(cdn_name)
            for data in http_data:
                if data:
                    if "CDN_NOT_RECOGNIZED" in data and len(cdns) == 0:
                        cdns.append("CDN_NOT_RECOGNIZED")
        except Exception as e:  # TODO fix exception usage
            print(e)
            error_code = 1

        return cdns, error_code
