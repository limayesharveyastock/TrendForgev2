"""
TrendForge v2
Indicator Engine

Master Indicator Pipeline
"""

from __future__ import annotations

import logging

import pandas as pd

from indicators.trend import TrendIndicators
from indicators.momentum import MomentumIndicators
from indicators.volatility import VolatilityIndicators
from indicators.volume import VolumeIndicators
from indicators.candlestick import CandlestickPatterns
from indicators.price_action import PriceAction

logger = logging.getLogger(__name__)


class IndicatorEngine:
    """
    Master Indicator Engine

    Calculates every indicator
    used by TrendForge.
    """

    def __init__(self):

        logger.info(
            "Indicator Engine initialized."
        )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    @staticmethod
    def validate(df: pd.DataFrame):

        required = [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        missing = [
            col
            for col in required
            if col not in df.columns
        ]

        if missing:

            raise ValueError(
                f"Missing columns: {missing}"
            )

    # --------------------------------------------------
    # Trend
    # --------------------------------------------------

    def add_trend(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        return TrendIndicators.add_all_emas(
            TrendIndicators.add_all_smas(df)
        )

    # --------------------------------------------------
    # Momentum
    # --------------------------------------------------

    def add_momentum(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        return MomentumIndicators.add_all(df)

    # --------------------------------------------------
    # Volatility
    # --------------------------------------------------

    def add_volatility(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        return VolatilityIndicators.add_all(df)

    # --------------------------------------------------
    # Volume
    # --------------------------------------------------

    def add_volume(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        return VolumeIndicators.add_all(df)

    # --------------------------------------------------
    # Candlestick
    # --------------------------------------------------

    def add_patterns(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        return CandlestickPatterns.add_all(df)

    # --------------------------------------------------
    # Price Action
    # --------------------------------------------------

    def add_price_action(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        return PriceAction.add_all(df)

    # --------------------------------------------------
    # Calculate Everything
    # --------------------------------------------------

    def calculate(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        self.validate(df)

        logger.info(
            "Calculating indicators..."
        )

        df = self.add_trend(df)

        df = self.add_momentum(df)

        df = self.add_volatility(df)

        df = self.add_volume(df)

        df = self.add_patterns(df)

        df = self.add_price_action(df)

        logger.info(
            "Indicator calculation complete."
        )

        return df

    # --------------------------------------------------
    # Last Candle
    # --------------------------------------------------

    @staticmethod
    def latest(
        df: pd.DataFrame,
    ) -> dict:

        return (
            df.iloc[-1]
            .to_dict()
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    @staticmethod
    def summary(
        df: pd.DataFrame,
    ) -> dict:

        latest = df.iloc[-1]

        return {

            "close":
            latest["close"],

            "ema20":
            latest.get("EMA_20"),

            "ema50":
            latest.get("EMA_50"),

            "ema200":
            latest.get("EMA_200"),

            "rsi":
            latest.get("RSI"),

            "macd":
            latest.get("MACD"),

            "adx":
            latest.get("ADX"),

            "atr":
            latest.get("ATR"),

            "rvol":
            latest.get("RVOL"),

            "breakout":
            latest.get("BREAKOUT"),

            "uptrend":
            latest.get("UPTREND"),

        }

    # --------------------------------------------------
    # Health
    # --------------------------------------------------

    def health(self):

        return {

            "status": "healthy",

            "trend": True,

            "momentum": True,

            "volatility": True,

            "volume": True,

            "candlestick": True,

            "price_action": True,

        }