from __future__ import annotations

from typing import Dict, Any

import math
import pandas as pd

from engines.base_engine import BaseEngine, EngineResult
from indicators.indicator_engine import IndicatorEngine


class TechnicalEngine(BaseEngine):

    NAME = "Technical Engine"

    def __init__(self, indicator_engine=None):
        self.indicators = indicator_engine or IndicatorEngine()

    @staticmethod
    def _num(row, key):
        try:
            value = float(row.get(key))
            return value if math.isfinite(value) else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _flag(row, key):
        value = row.get(key, False)
        return False if pd.isna(value) else bool(value)

    @staticmethod
    def _grade(score):

        if score >= 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"

        return "D"

    def evaluate(self, stock: Dict[str, Any]) -> EngineResult:

        df = stock.get("df")

        if not isinstance(df, pd.DataFrame):
            df = stock.get("data")

        if not isinstance(df, pd.DataFrame):

            return EngineResult(
                engine=self.NAME,
                passed=False,
                score=0,
                confidence=0,
                grade="D",
                warnings=[
                    "OHLCV DataFrame not supplied."
                ],
            )

        if len(df) < 30:

            return EngineResult(
                engine=self.NAME,
                passed=False,
                score=0,
                confidence=0,
                grade="D",
                warnings=[
                    "Minimum 30 candles required."
                ],
            )

        try:

            df = self.indicators.calculate(
                df.copy()
            )

        except Exception as exc:

            return EngineResult(
                engine=self.NAME,
                passed=False,
                score=0,
                confidence=0,
                grade="D",
                warnings=[
                    f"Indicator calculation failed: {exc}"
                ],
            )

        row = df.iloc[-1]
        previous = df.iloc[-2]

        trend_score, trend_reasons = (
            self._trend_score(row, previous)
        )

        momentum_score, momentum_reasons = (
            self._momentum_score(row, previous)
        )

        volume_score, volume_reasons = (
            self._volume_score(row, previous)
        )

        price_score, price_reasons = (
            self._price_action_score(row)
        )

        volatility_score, volatility_reasons = (
            self._volatility_score(row)
        )

        total = round(
            trend_score
            + momentum_score
            + volume_score
            + price_score
            + volatility_score,
            2,
        )

        reasons = (
            trend_reasons
            + momentum_reasons
            + volume_reasons
            + price_reasons
            + volatility_reasons
        )

        warnings = self._warnings(row)

        confidence = self._confidence(
            row,
            total,
        )

        return EngineResult(

            engine=self.NAME,

            passed=(
                total >= 70
                and not self._flag(
                    row,
                    "BREAKDOWN",
                )
            ),

            score=total,

            confidence=confidence,

            grade=self._grade(total),

            reasons=reasons,

            warnings=warnings,

            metrics={

                "close": self._num(
                    row,
                    "close",
                ),

                "EMA_9": self._num(
                    row,
                    "EMA_9",
                ),

                "EMA_20": self._num(
                    row,
                    "EMA_20",
                ),

                "EMA_50": self._num(
                    row,
                    "EMA_50",
                ),

                "EMA_100": self._num(
                    row,
                    "EMA_100",
                ),

                "EMA_200": self._num(
                    row,
                    "EMA_200",
                ),

                "RSI": self._num(
                    row,
                    "RSI",
                ),

                "MACD": self._num(
                    row,
                    "MACD",
                ),

                "MACD_SIGNAL": self._num(
                    row,
                    "MACD_SIGNAL",
                ),

                "MACD_HIST": self._num(
                    row,
                    "MACD_HIST",
                ),

                "ADX": self._num(
                    row,
                    "ADX",
                ),

                "+DI": self._num(
                    row,
                    "+DI",
                ),

                "-DI": self._num(
                    row,
                    "-DI",
                ),

                "RVOL": self._num(
                    row,
                    "RVOL",
                ),

                "VWAP": self._num(
                    row,
                    "VWAP",
                ),

                "CMF": self._num(
                    row,
                    "CMF",
                ),

                "MFI": self._num(
                    row,
                    "MFI",
                ),

                "ATR": self._num(
                    row,
                    "ATR",
                ),

                "ATR_PERCENT": self._num(
                    row,
                    "ATR_PERCENT",
                ),

                "BB_WIDTH": self._num(
                    row,
                    "BB_WIDTH",
                ),

                "SUPPORT": self._num(
                    row,
                    "SUPPORT",
                ),

                "RESISTANCE": self._num(
                    row,
                    "RESISTANCE",
                ),

                "BREAKOUT": self._flag(
                    row,
                    "BREAKOUT",
                ),

                "BREAKDOWN": self._flag(
                    row,
                    "BREAKDOWN",
                ),

                "UPTREND": self._flag(
                    row,
                    "UPTREND",
                ),

                "DOWNTREND": self._flag(
                    row,
                    "DOWNTREND",
                ),

            },
        )

    # --------------------------------------------------
    # TREND — 30 POINTS
    # --------------------------------------------------

    def _trend_score(self, row, previous):

        score = 0
        reasons = []

        close = self._num(row, "close")

        e9 = self._num(row, "EMA_9")
        e20 = self._num(row, "EMA_20")
        e50 = self._num(row, "EMA_50")
        e100 = self._num(row, "EMA_100")
        e200 = self._num(row, "EMA_200")

        if all(
            x is not None
            for x in (
                close,
                e9,
                e20,
                e50,
                e100,
                e200,
            )
        ):

            if e9 > e20 > e50 > e100 > e200:

                score += 12

                reasons.append(
                    "Full bullish EMA alignment"
                )

            elif e9 > e20 > e50:

                score += 8

                reasons.append(
                    "Bullish short/medium EMA alignment"
                )

            elif e20 < e50 < e200:

                reasons.append(
                    "Bearish EMA alignment"
                )

            if close > e20:

                score += 4

            if close > e50:

                score += 4

            if close > e200:

                score += 4

        if self._flag(row, "UPTREND"):

            score += 6

            reasons.append(
                "Higher-high / higher-low structure"
            )

        if self._flag(row, "DOWNTREND"):

            score -= 6

            reasons.append(
                "Lower-high / lower-low structure"
            )

        return max(0, min(30, score)), reasons

    # --------------------------------------------------
    # MOMENTUM — 25 POINTS
    # --------------------------------------------------

    def _momentum_score(self, row, previous):

        score = 0
        reasons = []

        rsi = self._num(row, "RSI")
        previous_rsi = self._num(
            previous,
            "RSI",
        )

        macd = self._num(row, "MACD")
        signal = self._num(
            row,
            "MACD_SIGNAL",
        )

        histogram = self._num(
            row,
            "MACD_HIST",
        )

        previous_histogram = self._num(
            previous,
            "MACD_HIST",
        )

        adx = self._num(
            row,
            "ADX",
        )

        plus_di = self._num(
            row,
            "+DI",
        )

        minus_di = self._num(
            row,
            "-DI",
        )

        # RSI

        if rsi is not None:

            if 55 <= rsi <= 70:

                score += 6

                reasons.append(
                    "RSI bullish momentum zone"
                )

            elif 50 <= rsi < 55:

                score += 3

            elif rsi < 30:

                score += 2

                reasons.append(
                    "RSI oversold"
                )

            elif rsi > 75:

                reasons.append(
                    "RSI overheated"
                )

            if (
                previous_rsi is not None
                and rsi > previous_rsi
            ):

                score += 3

                reasons.append(
                    "RSI rising"
                )

        # MACD

        if (
            macd is not None
            and signal is not None
        ):

            if macd > signal:

                score += 5

                reasons.append(
                    "MACD bullish"
                )

            else:

                score -= 2

        if histogram is not None:

            if histogram > 0:

                score += 3

            if (
                previous_histogram is not None
                and histogram > previous_histogram
            ):

                score += 2

                reasons.append(
                    "MACD histogram improving"
                )

        # ADX

        if adx is not None:

            if adx >= 25:

                score += 4

                reasons.append(
                    "ADX confirms trend strength"
                )

            elif adx >= 20:

                score += 2

        if (
            plus_di is not None
            and minus_di is not None
            and plus_di > minus_di
        ):

            score += 2

            reasons.append(
                "+DI above -DI"
            )

        return max(0, min(25, score)), reasons

    # --------------------------------------------------
    # VOLUME — 20 POINTS
    # --------------------------------------------------

    def _volume_score(self, row, previous):

        score = 0
        reasons = []

        rvol = self._num(
            row,
            "RVOL",
        )

        volume = self._num(
            row,
            "volume",
        )

        volume_sma = self._num(
            row,
            "VOL_SMA_20",
        )

        close = self._num(
            row,
            "close",
        )

        vwap = self._num(
            row,
            "VWAP",
        )

        cmf = self._num(
            row,
            "CMF",
        )

        obv = self._num(
            row,
            "OBV",
        )

        previous_obv = self._num(
            previous,
            "OBV",
        )

        if rvol is not None:

            if rvol >= 2:

                score += 7

                reasons.append(
                    "Strong volume expansion"
                )

            elif rvol >= 1.5:

                score += 5

                reasons.append(
                    "Above-average relative volume"
                )

            elif rvol >= 1:

                score += 3

        if (
            volume is not None
            and volume_sma is not None
            and volume > volume_sma
        ):

            score += 4

            reasons.append(
                "Volume above 20-period average"
            )

        if (
            close is not None
            and vwap is not None
            and close > vwap
        ):

            score += 4

            reasons.append(
                "Price above VWAP"
            )

        if cmf is not None:

            if cmf > 0:

                score += 3

                reasons.append(
                    "Positive CMF"
                )

        if (
            obv is not None
            and previous_obv is not None
            and obv > previous_obv
        ):

            score += 2

            reasons.append(
                "OBV confirms accumulation"
            )

        return max(0, min(20, score)), reasons

    # --------------------------------------------------
    # PRICE ACTION — 15 POINTS
    # --------------------------------------------------

    def _price_action_score(self, row):

        score = 0
        reasons = []

        if self._flag(
            row,
            "BREAKOUT",
        ):

            score += 8

            reasons.append(
                "20-period breakout"
            )

        if self._flag(
            row,
            "BREAKDOWN",
        ):

            score -= 8

            reasons.append(
                "20-period breakdown"
            )

        if self._flag(
            row,
            "UPTREND",
        ):

            score += 4

        close = self._num(
            row,
            "close",
        )

        resistance = self._num(
            row,
            "RESISTANCE",
        )

        support = self._num(
            row,
            "SUPPORT",
        )

        if (
            close is not None
            and resistance is not None
            and resistance > 0
        ):

            distance = (
                resistance - close
            ) / resistance

            if 0 <= distance <= 0.02:

                score += 3

                reasons.append(
                    "Price near resistance breakout zone"
                )

        if (
            close is not None
            and support is not None
            and support > 0
        ):

            distance = (
                close - support
            ) / close

            if 0 <= distance <= 0.02:

                reasons.append(
                    "Price near support"
                )

        return max(0, min(15, score)), reasons

    # --------------------------------------------------
    # VOLATILITY — 10 POINTS
    # --------------------------------------------------

    def _volatility_score(self, row):

        score = 0
        reasons = []

        atr_percent = self._num(
            row,
            "ATR_PERCENT",
        )

        bb_width = self._num(
            row,
            "BB_WIDTH",
        )

        if atr_percent is not None:

            if 1 <= atr_percent <= 4:

                score += 6

                reasons.append(
                    "Healthy trading volatility"
                )

            elif atr_percent < 1:

                score += 3

                reasons.append(
                    "Low volatility"
                )

            elif atr_percent <= 6:

                score += 2

            else:

                reasons.append(
                    "High volatility risk"
                )

        if bb_width is not None:

            if bb_width < 0.08:

                score += 4

                reasons.append(
                    "Volatility compression"
                )

        return max(0, min(10, score)), reasons

    # --------------------------------------------------
    # WARNINGS
    # --------------------------------------------------

    def _warnings(self, row):

        warnings = []

        rsi = self._num(
            row,
            "RSI",
        )

        rvol = self._num(
            row,
            "RVOL",
        )

        adx = self._num(
            row,
            "ADX",
        )

        if rsi is not None and rsi > 75:

            warnings.append(
                "RSI > 75: avoid chasing"
            )

        if rvol is not None and rvol < 0.75:

            warnings.append(
                "Weak relative volume"
            )

        if adx is not None and adx < 15:

            warnings.append(
                "ADX < 15: weak trend"
            )

        if self._flag(
            row,
            "BREAKDOWN",
        ):

            warnings.append(
                "Active breakdown"
            )

        return warnings

    # --------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------

    def _confidence(
        self,
        row,
        score,
    ):

        required = [

            "EMA_9",
            "EMA_20",
            "EMA_50",
            "EMA_100",
            "EMA_200",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
            "MACD_HIST",
            "ADX",
            "RVOL",
            "VWAP",
            "CMF",
            "MFI",
            "ATR",
            "ATR_PERCENT",

        ]

        available = 0

        for key in required:

            if self._num(row, key) is not None:

                available += 1

        completeness = (
            available /
            len(required)
        )

        confidence = (
            score *
            (
                0.70
                +
                0.30 * completeness
            )
        )

        return round(
            max(
                0,
                min(
                    100,
                    confidence,
                ),
            ),
            2,
        )

    def health(self):

        return {

            "status": "healthy",

            "engine": self.NAME,

            "components": {

                "trend": 30,

                "momentum": 25,

                "volume": 20,

                "price_action": 15,

                "volatility": 10,

            },

        }