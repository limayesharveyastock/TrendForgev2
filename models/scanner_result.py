from dataclasses import dataclass


@dataclass(slots=True)
class ScannerResult:

    symbol: str

    signal: str

    score: float

    confidence: float

    entry: float

    stoploss: float

    target1: float

    target2: float

    target3: float