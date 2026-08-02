from abc import ABC, abstractmethod
from typing import List

from models.sector_snapshot import SectorSnapshot


class SectorProvider(ABC):

    @abstractmethod
    def get_all_sectors(self) -> List[SectorSnapshot]:
        pass