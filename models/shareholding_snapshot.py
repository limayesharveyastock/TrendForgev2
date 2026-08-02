from dataclasses import dataclass
from typing import List

from models.shareholder import Shareholder


@dataclass
class ShareholdingSnapshot:

    symbol: str

    promoter: float

    fii: float

    dii: float

    mutual_fund: float

    insurance: float

    public: float

    shareholders: List[Shareholder]