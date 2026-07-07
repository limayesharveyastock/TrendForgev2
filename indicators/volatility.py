"""
TrendForge v2
Volatility Indicators
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class VolatilityIndicators:
    """
    Volatility Indicators

    ATR
    Bollinger Bands
    Keltner Channel
    """

    # --------------------------------------------------
    # ATR
    # --------------------------------------------------

    @staticmethod
    def add_atr(
        df: pd.DataFrame,
        length: int = 14,
    ) -> pd.DataFrame:

        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - df["close"].shift()).abs(),
                (df["low"] - df["close"].shift()).abs(),
            ],
            axis=1,
        ).max(axis=1)

        df["ATR"] = tr.rolling(length).mean()

        return df

    # --------------------------------------------------
    # Bollinger Bands
    # --------------------------------------------------

    @staticmethod
    def add_bollinger(
        df: pd.DataFrame,
        length: int = 20,
        std: float = 2.0,
    ) -> pd.DataFrame:

        sma = df["close"].rolling(length).mean()

        deviation = (
            df["close"]
            .rolling(length)
            .std()
        )

        df["BB_MID"] = sma

        df["BB_UPPER"] = (
            sma +
            deviation * std
        )

        df["BB_LOWER"] = (
            sma -
            deviation * std
        )

        df["BB_WIDTH"] = (
            (
                df["BB_UPPER"] -
                df["BB_LOWER"]
            )
            /
            sma
        )

        return df

    # --------------------------------------------------
    # EMA Helper
    # --------------------------------------------------

    @staticmethod
    def _ema(
        series,
        length,
    ):

        return series.ewm(
            span=length,
            adjust=False,
        ).mean()

    # --------------------------------------------------
    # Keltner Channel
    # --------------------------------------------------

    @staticmethod
    def add_keltner(
        df: pd.DataFrame,
        length: int = 20,
        multiplier: float = 2.0,
    ) -> pd.DataFrame:

        if "ATR" not in df.columns:

            df = VolatilityIndicators.add_atr(df)

        ema = VolatilityIndicators._ema(
            df["close"],
            length,
        )

        df["KC_MID"] = ema

        df["KC_UPPER"] = (
            ema +
            multiplier *
            df["ATR"]
        )

        df["KC_LOWER"] = (
            ema -
            multiplier *
            df["ATR"]
        )

        return df

    # --------------------------------------------------
    # ATR Percentage
    # --------------------------------------------------

    @staticmethod
    def add_atr_percent(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        if "ATR" not in df.columns:

            df = VolatilityIndicators.add_atr(df)

        df["ATR_PERCENT"] = (
            df["ATR"]
            /
            df["close"]
        ) * 100

        return df

    # --------------------------------------------------
    # All Indicators
    # --------------------------------------------------

    @staticmethod
    def add_all(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = VolatilityIndicators.add_atr(df)

        df = VolatilityIndicators.add_bollinger(df)

        df = VolatilityIndicators.add_keltner(df)

        df = VolatilityIndicators.add_atr_percent(df)

        return df