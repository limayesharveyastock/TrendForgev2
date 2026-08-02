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
from indicators.ema import EMAIndicator
from indicators.vwma import VWMAIndicator
from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator
from models.technical_snapshot import TechnicalSnapshot


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
class IndicatorEngine:

    def __init__(self):

        self.ema9 = EMAIndicator(9)
        self.ema20 = EMAIndicator(20)
        self.ema50 = EMAIndicator(50)
        self.ema100 = EMAIndicator(100)
        self.ema200 = EMAIndicator(200)

        self.vwma9 = VWMAIndicator(9)
        self.vwma26 = VWMAIndicator(26)

        self.rsi = RSIIndicator()

        self.macd = MACDIndicator()

    def build_snapshot(self, symbol, timeframe, df):

        ema9 = self.ema9.calculate(df).iloc[-1]
        ema20 = self.ema20.calculate(df).iloc[-1]
        ema50 = self.ema50.calculate(df).iloc[-1]
        ema100 = self.ema100.calculate(df).iloc[-1]
        ema200 = self.ema200.calculate(df).iloc[-1]

        vwma9 = self.vwma9.calculate(df).iloc[-1]
        vwma26 = self.vwma26.calculate(df).iloc[-1]

        rsi = self.rsi.calculate(df).iloc[-1]

        macd, signal, hist = self.macd.calculate(df)

        return TechnicalSnapshot(

            symbol=symbol,

            timeframe=timeframe,

            open=df.open.iloc[-1],
            high=df.high.iloc[-1],
            low=df.low.iloc[-1],
            close=df.close.iloc[-1],

            volume=df.volume.iloc[-1],

            ema9=ema9,
            ema20=ema20,
            ema50=ema50,
            ema100=ema100,
            ema200=ema200,

            vwma9=vwma9,
            vwma26=vwma26,

            vwap=None,

            rsi=rsi,

            macd=macd.iloc[-1],
            macd_signal=signal.iloc[-1],
            macd_histogram=hist.iloc[-1],

            adx=0,
            plus_di=0,
            minus_di=0,

            atr=0,

            obv=0,

            cmf=0,

            bb_upper=0,
            bb_middle=0,
            bb_lower=0
        )