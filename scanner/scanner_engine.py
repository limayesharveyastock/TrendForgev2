"""
TrendForge v2
Scanner Engine
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from indicators.indicator_engine import IndicatorEngine
from api.fundamentals import FundamentalService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ScanResult:
    @dataclass(slots=True)
class FundamentalScore:

    score: float

    reasons: list

    symbol: str

    score: float

    signal: str

    reasons: list

    latest: dict


class ScannerEngine:

    """
    Master Scanner
    """

    def __init__(
        self,
        fundamental_service: FundamentalService | None = None,
    ):

        self.indicators = IndicatorEngine()

        self.fundamentals = fundamental_service

        logger.info(
            "Scanner Engine initialized."
        )

    # --------------------------------------------------

    def calculate_indicators(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        return self.indicators.calculate(df)

    # --------------------------------------------------

    def latest(
        self,
        df: pd.DataFrame,
    ):

        return df.iloc[-1]

    # --------------------------------------------------

    def score_trend(
        self,
        latest,
    ):

        score = 0

        if latest["EMA_20"] > latest["EMA_50"]:

            score += 10

        if latest["EMA_50"] > latest["EMA_200"]:

            score += 10

        if latest["UPTREND"]:

            score += 10

        return score

    # --------------------------------------------------

    def score_momentum(
        self,
        latest,
    ):

        score = 0

        if 55 < latest["RSI"] < 70:

            score += 10

        if latest["MACD"] > latest["MACD_SIGNAL"]:

            score += 10

        if latest["ADX"] > 25:

            score += 10

        return score

    # --------------------------------------------------

    def score_volume(
        self,
        latest,
    ):

        score = 0

        if latest["RVOL"] > 1.5:

            score += 10

        if latest["CMF"] > 0:

            score += 10

        return score

    # --------------------------------------------------

    def score_price_action(
        self,
        latest,
    ):
    def score_fundamentals(
    self,
    symbol: str,
):

    if self.fundamentals is None:

        return FundamentalScore(
            0,
            [],
        )

    try:

        f = self.fundamentals.get(symbol)

    except Exception:

        return FundamentalScore(
            0,
            [],
        )

    score = 0

    reasons = []

    if 0 < f.pe < 30:

        score += 5

        reasons.append("Healthy PE")

    if f.roe > 15:

        score += 5

        reasons.append("ROE >15%")

    if f.roce > 15:

        score += 5

        reasons.append("ROCE >15%")

    if f.debt_to_equity < 0.5:

        score += 5

        reasons.append("Low Debt")

    if f.sales_growth > 10:

        score += 5

        reasons.append("Sales Growth")

    if f.profit_growth > 10:

        score += 5

        reasons.append("Profit Growth")

    return FundamentalScore(
        score,
        reasons,
    )
        score = 0

        if latest["BREAKOUT"]:

            score += 15

        if latest["GAP_UP"]:

            score += 5

        if latest["BULLISH_ENGULFING"]:

            score += 10

        return score

    # --------------------------------------------------

    def total_score(
        self,
        latest,
    ):

        score = 0

        score += self.score_trend(latest)

        score += self.score_momentum(latest)

        score += self.score_volume(latest)

        score += self.score_price_action(latest)

        return min(score,100)

    # --------------------------------------------------

    def signal(
        self,
        score,
    ):
    def rank(
    self,
    results,
    ):
    def filter_signal(
    self,
    results,
    signal,
):

    return [

        r

        for r in results

        if r.signal == signal

    ]
    def top_n(
    self,
    results,
    n=20,
):
    def summary(
    self,
    results,
):

    return {

        "total":

        len(results),

        "strong_buy":

        len(

            self.filter_signal(

                results,

                "STRONG BUY",

            )

        ),

        "buy":

        len(

            self.filter_signal(

                results,

                "BUY",

            )

        ),

        "watch":

        len(

            self.filter_signal(

                results,

                "WATCH",

            )

        ),

    }
    return self.rank(
        results
    )[:n]

    return sorted(

        results,

        key=lambda x: x.score,

        reverse=True,

    )
        if score >= 80:

            return "STRONG BUY"

        if score >= 60:

            return "BUY"

        if score >= 40:

            return "WATCH"

        return "IGNORE"

    # --------------------------------------------------

    def scan(
        self,
        symbol: str,
        df: pd.DataFrame,
    ) -> ScanResult:

        df = self.calculate_indicators(df)

        latest = self.latest(df)

        score = self.total_score(latest)

        fundamental = self.score_fundamentals(
        symbol,)

score += fundamental.score

score = min(score, 100)

        signal = self.signal(score)

        reasons = []
        reasons.extend(
        fundamental.reasons)

        if latest["BREAKOUT"]:

            reasons.append(
                "20-Day Breakout"
            )

        if latest["RVOL"] > 1.5:

            reasons.append(
                "High Relative Volume"
            )

        if latest["MACD"] > latest["MACD_SIGNAL"]:

            reasons.append(
                "MACD Bullish"
            )

        if latest["RSI"] > 55:

            reasons.append(
                "Strong RSI"
            )

        return ScanResult(

            symbol=symbol,

            score=score,

            signal=signal,

            reasons=reasons,

            latest=latest.to_dict(),

        )