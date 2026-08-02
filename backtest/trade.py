from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Trade:

    symbol: str

    entry_date: datetime

    exit_date: datetime

    entry_price: float

    exit_price: float

    quantity: int

    side: str

    pnl: float

    pnl_percent: float

    stoploss: float

    target: float

    strategy: str