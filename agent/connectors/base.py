"""Base abstract connector for sourcing recruitment data."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseConnector(ABC):
    """Abstract connector interface for job discovery and signal sourcing."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the data source (e.g. 'LinkedIn Posts', 'Naukri', 'Company Careers')."""
        pass

    @abstractmethod
    def search_jobs(self, query: str, location: str = "Hyderabad", limit: int = 10) -> List[Dict[str, Any]]:
        """Search for job opportunities."""
        pass

    @abstractmethod
    def search_signals(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for active recruitment signals, walk-ins, off-campus drives, and referral posts."""
        pass
