from dataclasses import dataclass


@dataclass
class MarketSnapshot:

    nifty50: float

    banknifty: float

    midcap: float

    smallcap: float

    india_vix: float

    advances: int

    declines: int

    unchanged: int

    fii_cash: float

    dii_cash: float

    above20ema: float

    above50ema: float

    above200ema: float

    timestamp: str