"""
TrendForge v2
Trend Indicators
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class TrendIndicators:
    """
    Trend Indicators

    EMA
    SMA
    """

    @staticmethod
    def ema(
        df: pd.DataFrame,
        length: int,
    ) -> pd.Series:

        return df["close"].ewm(
            span=length,
            adjust=False,
        ).mean()

    @staticmethod
    def sma(
        df: pd.DataFrame,
        length: int,
    ) -> pd.Series:

        return (
            df["close"]
            .rolling(length)
            .mean()
        )

    @staticmethod
    def add_ema(
        df: pd.DataFrame,
        length: int,
    ) -> pd.DataFrame:

        df[f"EMA_{length}"] = (
            TrendIndicators.ema(
                df,
                length,
            )
        )

        return df

    @staticmethod
    def add_sma(
        df: pd.DataFrame,
        length: int,
    ) -> pd.DataFrame:

        df[f"SMA_{length}"] = (
            TrendIndicators.sma(
                df,
                length,
            )
        )

        return df

    @staticmethod
    def add_all_emas(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        for length in (
            9,
            20,
            50,
            100,
            200,
        ):

            df = TrendIndicators.add_ema(
                df,
                length,
            )

        return df

    @staticmethod
    def add_all_smas(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        for length in (
            20,
            50,
            100,
            200,
        ):

            df = TrendIndicators.add_sma(
                df,
                length,
            )

        return df