from abc import ABC, abstractmethod
from typing import Dict, Optional


class FundamentalProvider(ABC):
    """
    Base class for all fundamental data providers.
    """

    @abstractmethod
    def get_fundamentals(self, symbol: str) -> Optional[Dict]:
        raise NotImplementedError