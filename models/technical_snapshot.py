from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class TechnicalSnapshot:

    symbol: str

    timeframe: str

    close: float

    high: float

    low: float

    open: float

    volume: float

    ema9: float
    ema20: float
    ema50: float
    ema100: float
    ema200: float

    vwma9: float
    vwma26: float

    vwap: Optional[float]

    rsi: float

    macd: float
    macd_signal: float
    macd_histogram: float

    adx: float
    plus_di: float
    minus_di: float

    atr: float

    obv: float

    cmf: float

    bb_upper: float
    bb_middle: float
    bb_lower: float