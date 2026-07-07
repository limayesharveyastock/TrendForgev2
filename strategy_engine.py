"""
strategy_engine.py
--------------------------------------------------------
TrendForge Strategy Engine

Responsibilities
----------------
- Collect indicator signals
- Apply configurable weights
- Calculate confidence score
- Generate BUY / SELL / HOLD signal
- Return detailed decision breakdown
"""

from dataclasses import dataclass, field
from typing import Dict, List


# ======================================================
# INDICATOR SIGNAL
# ======================================================

@dataclass
class IndicatorSignal:

    name: str

    signal: str      # BUY / SELL / NEUTRAL

    confidence: float = 1.0

    weight: float = 1.0


# ======================================================
# STRATEGY RESULT
# ======================================================

@dataclass
class StrategyResult:

    symbol: str

    action: str

    score: float

    buy_score: float

    sell_score: float

    confidence: float

    signals: List[IndicatorSignal] = field(default_factory=list)


# ======================================================
# STRATEGY ENGINE
# ======================================================

class StrategyEngine:

    def __init__(self):

        self.buy_threshold = 70

        self.sell_threshold = 70

    # --------------------------------------------------

    def evaluate(
        self,
        symbol: str,
        signals: List[IndicatorSignal]
    ) -> StrategyResult:

        buy = 0.0

        sell = 0.0

        total_weight = 0.0

        for signal in signals:

            score = signal.weight * signal.confidence

            total_weight += signal.weight

            if signal.signal.upper() == "BUY":

                buy += score

            elif signal.signal.upper() == "SELL":

                sell += score

        if total_weight == 0:

            confidence = 0

        else:

            confidence = round(
                max(buy, sell) * 100 / total_weight,
                2
            )

        if confidence >= self.buy_threshold and buy > sell:

            action = "BUY"

        elif confidence >= self.sell_threshold and sell > buy:

            action = "SELL"

        else:

            action = "HOLD"

        return StrategyResult(

            symbol=symbol,

            action=action,

            score=round(buy - sell, 2),

            buy_score=round(buy, 2),

            sell_score=round(sell, 2),

            confidence=confidence,

            signals=signals
        )

    # --------------------------------------------------

    def rank(
        self,
        stock_signals: Dict[str, List[IndicatorSignal]]
    ):

        results = []

        for symbol, signals in stock_signals.items():

            results.append(

                self.evaluate(
                    symbol,
                    signals
                )

            )

        results.sort(

            key=lambda x: x.confidence,

            reverse=True

        )

        return results

    # --------------------------------------------------

    def summary(
        self,
        result: StrategyResult
    ):

        return {

            "Symbol": result.symbol,

            "Action": result.action,

            "Confidence": result.confidence,

            "Buy Score": result.buy_score,

            "Sell Score": result.sell_score,

            "Net Score": result.score
        }