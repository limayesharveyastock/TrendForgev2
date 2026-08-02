from abc import ABC, abstractmethod

from models.market_snapshot import MarketSnapshot


class MarketProvider(ABC):

    @abstractmethod
    def get_snapshot(self) -> MarketSnapshot:

        pass