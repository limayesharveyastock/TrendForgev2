"""
TrendForge v2
Base Provider
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.fundamentals import FundamentalData


class BaseProvider(ABC):
    """
    Base class for all
    fundamental providers.
    """

    @abstractmethod
    def get_fundamentals(
        self,
        symbol: str,
    ) -> FundamentalData:
        """
        Returns fundamentals
        for a company.
        """
        raise NotImplementedError