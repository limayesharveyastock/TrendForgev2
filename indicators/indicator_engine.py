"""
TrendForge v2 - Master Indicator Engine

Single, unified indicator pipeline.

Preserves:
- EMA 9
- EMA 20
- EMA 50
- EMA 100
- EMA 200
- VWMA 9
- VWMA 26
- RSI
- MACD

Also runs the existing:
- Trend
- Momentum
- Volatility
- Volume
- Candlestick
- Price Action
modules.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from indicators.trend import TrendIndicators
from indicators.momentum import MomentumIndicators
from indicators.volatility import VolatilityIndicators
from indicators.volume import VolumeIndicators
from indicators.candlestick import CandlestickPatterns
from indicators.price_action import PriceAction

from indicators.ema import EMAIndicator
from indicators.vwma import VWMAIndicator
from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator


logger = logging.getLogger(__name__)


class IndicatorEngine:
    """
    Master technical indicator engine.

    This class is the SINGLE entry point for technical calculations
    throughout TrendForge.
    """

    REQUIRED_COLUMNS = (
        "open",
        "high",
        "low",
        "close",
        "volume",
    )

    def __init__(self) -> None:

        # ==================================================
        # EMA
        # ==================================================

        self.ema9 = EMAIndicator(9)
        self.ema20 = EMAIndicator(20)
        self.ema50 = EMAIndicator(50)
        self.ema100 = EMAIndicator(100)
        self.ema200 = EMAIndicator(200)

        # ==================================================
        # VWMA
        # ==================================================

        self.vwma9 = VWMAIndicator(9)
        self.vwma26 = VWMAIndicator(26)

        # ==================================================
        # MOMENTUM
        # ==================================================

        self.rsi = RSIIndicator()
        self.macd = MACDIndicator()

        logger.info("Indicator Engine initialized")

    # ======================================================
    # VALIDATION
    # ======================================================

    @classmethod
    def validate(cls, df: pd.DataFrame) -> None:

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "df must be a pandas DataFrame"
            )

        if df.empty:
            raise ValueError(
                "Cannot calculate indicators on empty DataFrame"
            )

        missing = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required OHLCV columns: {missing}"
            )

    # ======================================================
    # COLUMN NORMALIZATION
    # ======================================================

    @staticmethod
    def normalize_columns(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result.columns = [
            str(column).lower()
            for column in result.columns
        ]

        return result

    # ======================================================
    # COMPLETE CALCULATION PIPELINE
    # ======================================================

    def calculate(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = self.normalize_columns(df)

        self.validate(df)

        logger.debug(
            "Starting indicator calculation"
        )

        # ==================================================
        # TREND
        # ==================================================

        df = TrendIndicators.add_all_smas(df)

        df = TrendIndicators.add_all_emas(df)

        # ==================================================
        # MOMENTUM
        # ==================================================

        df = MomentumIndicators.add_all(df)

        # ==================================================
        # VOLATILITY
        # ==================================================

        df = VolatilityIndicators.add_all(df)

        # ==================================================
        # VOLUME
        # ==================================================

        df = VolumeIndicators.add_all(df)

        # ==================================================
        # CANDLESTICK
        # ==================================================

        df = CandlestickPatterns.add_all(df)

        # ==================================================
        # PRICE ACTION
        # ==================================================

        df = PriceAction.add_all(df)

        # ==================================================
        # CORE EMA ENGINE
        # ==================================================

        df["EMA_9"] = self.ema9.calculate(df)

        df["EMA_20"] = self.ema20.calculate(df)

        df["EMA_50"] = self.ema50.calculate(df)

        df["EMA_100"] = self.ema100.calculate(df)

        df["EMA_200"] = self.ema200.calculate(df)

        # ==================================================
        # CORE VWMA ENGINE
        # ==================================================

        df["VWMA_9"] = self.vwma9.calculate(df)

        df["VWMA_26"] = self.vwma26.calculate(df)

        # ==================================================
        # RSI
        # ==================================================

        rsi = self.rsi.calculate(df)

        if isinstance(rsi, pd.Series):
            df["RSI"] = rsi
        else:
            df["RSI"] = pd.Series(
                rsi,
                index=df.index,
            )

        # ==================================================
        # MACD
        # ==================================================

        macd, signal, histogram = (
            self.macd.calculate(df)
        )

        df["MACD"] = macd

        df["MACD_SIGNAL"] = signal

        df["MACD_HISTOGRAM"] = histogram

        logger.debug(
            "Indicator calculation complete: %d rows",
            len(df),
        )

        return df

    # ======================================================
    # LATEST CANDLE
    # ======================================================

    @staticmethod
    def latest(
        df: pd.DataFrame,
    ) -> dict[str, Any]:

        if df.empty:
            return {}

        return (
            df.iloc[-1]
            .to_dict()
        )

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def build_snapshot(
        self,
        symbol: str,
        timeframe: str,
        df: pd.DataFrame,
    ) -> dict[str, Any]:

        calculated = self.calculate(df)

        latest = calculated.iloc[-1]

        return {

            "symbol": symbol,

            "timeframe": timeframe,

            "open": latest.get("open"),

            "high": latest.get("high"),

            "low": latest.get("low"),

            "close": latest.get("close"),

            "volume": latest.get("volume"),

            # EMA
            "ema9": latest.get("EMA_9"),

            "ema20": latest.get("EMA_20"),

            "ema50": latest.get("EMA_50"),

            "ema100": latest.get("EMA_100"),

            "ema200": latest.get("EMA_200"),

            # VWMA
            "vwma9": latest.get("VWMA_9"),

            "vwma26": latest.get("VWMA_26"),

            # VWAP
            "vwap": latest.get("VWAP"),

            # Momentum
            "rsi": latest.get("RSI"),

            "macd": latest.get("MACD"),

            "macd_signal": latest.get(
                "MACD_SIGNAL"
            ),

            "macd_histogram": latest.get(
                "MACD_HISTOGRAM"
            ),

            # Trend
            "adx": latest.get("ADX"),

            "plus_di": latest.get("PLUS_DI"),

            "minus_di": latest.get("MINUS_DI"),

            # Volatility
            "atr": latest.get("ATR"),

            # Volume
            "rvol": latest.get("RVOL"),

            "obv": latest.get("OBV"),

            "cmf": latest.get("CMF"),

            # Bollinger Bands
            "bb_upper": latest.get(
                "BB_UPPER"
            ),

            "bb_middle": latest.get(
                "BB_MIDDLE"
            ),

            "bb_lower": latest.get(
                "BB_LOWER"
            ),

            # Price action
            "breakout": latest.get(
                "BREAKOUT"
            ),

            "breakdown": latest.get(
                "BREAKDOWN"
            ),

            "uptrend": latest.get(
                "UPTREND"
            ),

            "downtrend": latest.get(
                "DOWNTREND"
            ),
        }

    # ======================================================
    # SUMMARY
    # ======================================================

    @staticmethod
    def summary(
        df: pd.DataFrame,
    ) -> dict[str, Any]:

        if df.empty:
            return {}

        latest = df.iloc[-1]

        return {

            "close":
                latest.get("close"),

            # EMA
            "ema9":
                latest.get("EMA_9"),

            "ema20":
                latest.get("EMA_20"),

            "ema50":
                latest.get("EMA_50"),

            "ema100":
                latest.get("EMA_100"),

            "ema200":
                latest.get("EMA_200"),

            # VWMA
            "vwma9":
                latest.get("VWMA_9"),

            "vwma26":
                latest.get("VWMA_26"),

            # VWAP
            "vwap":
                latest.get("VWAP"),

            # Momentum
            "rsi":
                latest.get("RSI"),

            "macd":
                latest.get("MACD"),

            "macd_signal":
                latest.get("MACD_SIGNAL"),

            # Trend
            "adx":
                latest.get("ADX"),

            # Volatility
            "atr":
                latest.get("ATR"),

            # Volume
            "rvol":
                latest.get("RVOL"),

            # Price Action
            "breakout":
                latest.get("BREAKOUT"),

            "breakdown":
                latest.get("BREAKDOWN"),

            "uptrend":
                latest.get("UPTREND"),

            "downtrend":
                latest.get("DOWNTREND"),
        }

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def health(self) -> dict[str, Any]:

        return {

            "status": "healthy",

            "trend": True,

            "momentum": True,

            "volatility": True,

            "volume": True,

            "candlestick": True,

            "price_action": True,

            "ema_9": True,

            "ema_20": True,

            "ema_50": True,

            "ema_100": True,

            "ema_200": True,

            "vwma_9": True,

            "vwma_26": True,

            "rsi": True,

            "macd": True,
        }