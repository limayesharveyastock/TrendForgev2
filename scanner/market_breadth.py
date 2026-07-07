"""
market_breadth.py
----------------------------------------------------------
TrendForge Market Breadth Engine

Features
--------
- Advance / Decline Statistics
- Advance / Decline Ratio
- Advance / Decline Line
- New High / New Low Analysis
- Stocks Above EMA20
- Stocks Above EMA50
- Stocks Above EMA200
- Sector Strength Ranking
- Breadth Score
"""

from dataclasses import dataclass
from typing import List, Dict


# ==========================================================
# STOCK DATA
# ==========================================================

@dataclass
class BreadthStock:

    symbol: str

    sector: str

    close: float

    ema20: float

    ema50: float

    ema200: float

    is_new_high: bool

    is_new_low: bool

    change_percent: float


# ==========================================================
# RESULT
# ==========================================================

@dataclass
class BreadthResult:

    advances: int

    declines: int

    unchanged: int

    advance_decline_ratio: float

    advance_decline_line: int

    new_highs: int

    new_lows: int

    above_ema20: float

    above_ema50: float

    above_ema200: float

    breadth_score: float

    sector_strength: Dict[str, float]


# ==========================================================
# ENGINE
# ==========================================================

class MarketBreadth:

    def calculate(self, stocks: List[BreadthStock]) -> BreadthResult:

        total = len(stocks)

        if total == 0:
            raise ValueError("No market data supplied.")

        advances = sum(
            1 for s in stocks
            if s.change_percent > 0
        )

        declines = sum(
            1 for s in stocks
            if s.change_percent < 0
        )

        unchanged = total - advances - declines

        ratio = round(
            advances / max(declines, 1),
            2
        )

        ad_line = advances - declines

        new_highs = sum(
            1 for s in stocks
            if s.is_new_high
        )

        new_lows = sum(
            1 for s in stocks
            if s.is_new_low
        )

        ema20 = round(
            sum(
                1 for s in stocks
                if s.close > s.ema20
            ) * 100 / total,
            2
        )

        ema50 = round(
            sum(
                1 for s in stocks
                if s.close > s.ema50
            ) * 100 / total,
            2
        )

        ema200 = round(
            sum(
                1 for s in stocks
                if s.close > s.ema200
            ) * 100 / total,
            2
        )

        sector_strength = self._sector_strength(stocks)

        breadth_score = round(
            (
                ratio * 20
                +
                ema20 * 0.15
                +
                ema50 * 0.30
                +
                ema200 * 0.35
            ),
            2
        )

        return BreadthResult(

            advances=advances,

            declines=declines,

            unchanged=unchanged,

            advance_decline_ratio=ratio,

            advance_decline_line=ad_line,

            new_highs=new_highs,

            new_lows=new_lows,

            above_ema20=ema20,

            above_ema50=ema50,

            above_ema200=ema200,

            breadth_score=breadth_score,

            sector_strength=sector_strength

        )

    # ------------------------------------------------------

    def _sector_strength(
        self,
        stocks: List[BreadthStock]
    ) -> Dict[str, float]:

        sectors = {}

        for stock in stocks:

            sectors.setdefault(
                stock.sector,
                []
            ).append(stock.change_percent)

        ranking = {}

        for sector, changes in sectors.items():

            ranking[sector] = round(

                sum(changes) / len(changes),

                2

            )

        return dict(

            sorted(

                ranking.items(),

                key=lambda x: x[1],

                reverse=True

            )

        )

    # ------------------------------------------------------

    def summary(
        self,
        result: BreadthResult
    ):

        return {

            "Advances": result.advances,

            "Declines": result.declines,

            "Advance/Decline Ratio":
                result.advance_decline_ratio,

            "Advance/Decline Line":
                result.advance_decline_line,

            "New Highs":
                result.new_highs,

            "New Lows":
                result.new_lows,

            "% Above EMA20":
                result.above_ema20,

            "% Above EMA50":
                result.above_ema50,

            "% Above EMA200":
                result.above_ema200,

            "Breadth Score":
                result.breadth_score,

            "Sector Strength":
                result.sector_strength

        }