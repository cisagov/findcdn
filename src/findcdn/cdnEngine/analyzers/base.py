"""Analyzer base class for templatnig new analyzers."""

# Standard Python Libraries
from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import List, Tuple, Union

# Third-Party Libraries
from loguru import logger

# Internal Libraries


@dataclass
class Domain:
    """Domain class for representing domains processed."""

    domain: str
    ips: List[Union[str, IPv4Address, IPv6Address]]
    cnames: List[str]
    cdns: List[str]


class BaseAnalyzer(ABC):
    """This is the base class for all analyzers used for FindCDN."""

    __NAME = "BaseAnalyzer"

    @abstractclassmethod
    def get_data(self, domain: Domain) -> Tuple[List, int]:
        """Perform action to get data we need to detect a CDN."""
        pass

    @abstractclassmethod
    def parse(self, data: List) -> Tuple[List, int]:
        """Parse the data gathered and return CDN results."""
        pass

    def run(self, domain: Domain, timeout: int = 10, verbose: bool = False) -> Tuple[List[str], Domain, int]:
        """Kick off analysis and return CDN results."""
        self.timeout = timeout

        if verbose:
            logger.debug(f"[{self.__NAME}] Obtaining data")
        data, err = self.get_data(domain)
        if err:
            return [], domain, err

        if verbose:
            logger.debug(f"[{self.__NAME}] Parsing results ")
        results, err = self.parse(data)
        if err:
            return [], domain, err

        results = list(set(results))

        return results, domain, 0
