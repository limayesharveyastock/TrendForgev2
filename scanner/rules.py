"""
TrendForge v2
Scanner Rules Engine

Purpose:
    Convert indicator/fundamental data into deterministic boolean rules.

Architecture:
    Indicator Engine
        ↓
    ScannerRules
        ↓
    Scoring Engine
        ↓
    Signal Engine

Rules are intentionally deterministic.
No data fetching is performed here.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


class ScannerRules:

    # =========================================================
    # SAFE HELPERS
    # =========================================================

    @staticmethod
    def _get(
        data: Any,
        key: str,
        default: Any = None,
    ) -> Any:

        if data is None:
            return default

        if isinstance(data, dict):
            return data.get(key, default)

        try:
            return data.get(key, default)
        except Exception:
            pass

        return getattr(
            data,
            key,
            default,
        )

    @staticmethod
    def _number(
        data: Any,
        key: str,
        default: float = 0.0,
    ) -> float:

        value = ScannerRules._get(
            data,
            key,
            default,
        )

        try:
            if pd.isna(value):
                return default

            return float(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _bool(
        data: Any,
        key: str,
        default: bool = False,
    ) -> bool:

        value = ScannerRules._get(
            data,
            key,
            default,
        )

        if pd.isna(value) if not isinstance(value, bool) else False:
            return default

        return bool(value)

    # =========================================================
    # TREND
    # =========================================================

    @staticmethod
    def ema_bullish(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "EMA_20")
            >
            ScannerRules._number(latest, "EMA_50")
            >
            ScannerRules._number(latest, "EMA_200")
        )

    @staticmethod
    def ema_bearish(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "EMA_20")
            <
            ScannerRules._number(latest, "EMA_50")
            <
            ScannerRules._number(latest, "EMA_200")
        )

    @staticmethod
    def golden_cross(latest: Any) -> bool:

        ema50 = ScannerRules._number(
            latest,
            "EMA_50",
        )

        ema200 = ScannerRules._number(
            latest,
            "EMA_200",
        )

        return ema50 > ema200

    @staticmethod
    def death_cross(latest: Any) -> bool:

        ema50 = ScannerRules._number(
            latest,
            "EMA_50",
        )

        ema200 = ScannerRules._number(
            latest,
            "EMA_200",
        )

        return ema50 < ema200

    @staticmethod
    def ema9_above_26(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "EMA_9")
            >
            ScannerRules._number(latest, "EMA_26")
        )

    @staticmethod
    def ema9_below_26(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "EMA_9")
            <
            ScannerRules._number(latest, "EMA_26")
        )

    @staticmethod
    def vwma9_above_26(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "VWMA_9")
            >
            ScannerRules._number(latest, "VWMA_26")
        )

    @staticmethod
    def vwma9_below_26(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "VWMA_9")
            <
            ScannerRules._number(latest, "VWMA_26")
        )

    # =========================================================
    # MOMENTUM
    # =========================================================

    @staticmethod
    def rsi_bullish(latest: Any) -> bool:

        rsi = ScannerRules._number(
            latest,
            "RSI",
        )

        return 55 <= rsi <= 70

    @staticmethod
    def rsi_bearish(latest: Any) -> bool:

        rsi = ScannerRules._number(
            latest,
            "RSI",
        )

        return 30 <= rsi <= 45

    @staticmethod
    def rsi_oversold(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "RSI",
            )
            < 30
        )

    @staticmethod
    def rsi_overbought(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "RSI",
            )
            > 70
        )

    @staticmethod
    def macd_bullish(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "MACD")
            >
            ScannerRules._number(latest, "MACD_SIGNAL")
        )

    @staticmethod
    def macd_bearish(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "MACD")
            <
            ScannerRules._number(latest, "MACD_SIGNAL")
        )

    @staticmethod
    def adx_strong(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "ADX",
            )
            > 25
        )

    # =========================================================
    # VOLUME / MONEY FLOW
    # =========================================================

    @staticmethod
    def high_volume(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "RVOL",
            )
            >= 2
        )

    @staticmethod
    def medium_volume(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "RVOL",
            )
            >= 1.5
        )

    @staticmethod
    def low_volume(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "RVOL",
            )
            < 1
        )

    @staticmethod
    def positive_money_flow(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "CMF",
            )
            > 0
        )

    @staticmethod
    def negative_money_flow(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "CMF",
            )
            < 0
        )

    @staticmethod
    def above_vwap(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "close")
            >
            ScannerRules._number(latest, "VWAP")
        )

    @staticmethod
    def below_vwap(latest: Any) -> bool:

        return (
            ScannerRules._number(latest, "close")
            <
            ScannerRules._number(latest, "VWAP")
        )

    # =========================================================
    # VOLATILITY
    # =========================================================

    @staticmethod
    def atr_expansion(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "ATR_PERCENT",
            )
            > 2
        )

    @staticmethod
    def bb_squeeze(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "BB_WIDTH",
            )
            < 0.08
        )

    # =========================================================
    # PRICE ACTION
    # =========================================================

    @staticmethod
    def breakout(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "BREAKOUT",
        )

    @staticmethod
    def breakdown(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "BREAKDOWN",
        )

    @staticmethod
    def gap_up(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "GAP_UP",
        )

    @staticmethod
    def gap_down(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "GAP_DOWN",
        )

    @staticmethod
    def uptrend(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "UPTREND",
        )

    @staticmethod
    def downtrend(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "DOWNTREND",
        )

    @staticmethod
    def inside_bar(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "INSIDE_BAR",
        )

    @staticmethod
    def nr7(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "NR7",
        )

    # =========================================================
    # CANDLESTICKS
    # =========================================================

    @staticmethod
    def bullish_engulfing(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "BULLISH_ENGULFING",
        )

    @staticmethod
    def bearish_engulfing(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "BEARISH_ENGULFING",
        )

    @staticmethod
    def hammer(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "HAMMER",
        )

    @staticmethod
    def doji(latest: Any) -> bool:

        return ScannerRules._bool(
            latest,
            "DOJI",
        )

    # =========================================================
    # FUNDAMENTALS
    # =========================================================

    @staticmethod
    def strong_fundamentals(f: Any) -> bool:

        return (
            ScannerRules._number(f, "roe") >= 15
            and
            ScannerRules._number(f, "roce") >= 15
            and
            ScannerRules._number(
                f,
                "debt_to_equity",
                999,
            ) < 0.5
            and
            ScannerRules._number(
                f,
                "sales_growth",
            ) > 10
            and
            ScannerRules._number(
                f,
                "profit_growth",
            ) > 10
        )

    @staticmethod
    def value_stock(f: Any) -> bool:

        pe = ScannerRules._number(
            f,
            "pe",
        )

        pb = ScannerRules._number(
            f,
            "pb",
            999,
        )

        return (
            0 < pe < 25
            and
            0 < pb < 5
        )

    @staticmethod
    def quality_stock(f: Any) -> bool:

        return (
            ScannerRules._number(f, "roe") > 20
            and
            ScannerRules._number(f, "roce") > 20
        )

    @staticmethod
    def strong_growth(f: Any) -> bool:

        return (
            ScannerRules._number(
                f,
                "sales_growth",
            ) >= 20
            and
            ScannerRules._number(
                f,
                "profit_growth",
            ) >= 20
        )

    @staticmethod
    def multibagger_filter(f: Any) -> bool:

        return (
            ScannerRules._number(f, "roe") >= 20
            and
            ScannerRules._number(f, "roce") >= 20
            and
            ScannerRules._number(
                f,
                "debt_to_equity",
                999,
            ) <= 0.30
            and
            ScannerRules._number(
                f,
                "sales_growth",
            ) >= 15
            and
            ScannerRules._number(
                f,
                "profit_growth",
            ) >= 15
        )

    # =========================================================
    # STRATEGY COMBINATIONS
    # =========================================================

    @staticmethod
    def breakout_buy(latest: Any) -> bool:

        return (
            ScannerRules.breakout(latest)
            and
            ScannerRules.ema_bullish(latest)
            and
            ScannerRules.macd_bullish(latest)
            and
            ScannerRules.high_volume(latest)
        )

    @staticmethod
    def swing_buy(latest: Any) -> bool:

        return (
            ScannerRules.uptrend(latest)
            and
            ScannerRules.rsi_bullish(latest)
            and
            ScannerRules.medium_volume(latest)
        )

    @staticmethod
    def intraday_buy(latest: Any) -> bool:

        return (
            ScannerRules.above_vwap(latest)
            and
            ScannerRules.high_volume(latest)
            and
            ScannerRules.macd_bullish(latest)
        )

    @staticmethod
    def reversal_buy(latest: Any) -> bool:

        return (
            ScannerRules.rsi_oversold(latest)
            and
            ScannerRules.hammer(latest)
        )

    @staticmethod
    def positional_buy(latest: Any) -> bool:

        return (
            ScannerRules.ema_bullish(latest)
            and
            ScannerRules.breakout(latest)
            and
            ScannerRules.adx_strong(latest)
        )

    # =========================================================
    # EMA CROSSOVERS
    # =========================================================

    @staticmethod
    def ema20_cross_above_50(
        df: pd.DataFrame,
    ) -> bool:

        if len(df) < 2:
            return False

        return bool(
            (
                (df["EMA_20"].shift(1) <= df["EMA_50"].shift(1))
                &
                (df["EMA_20"] > df["EMA_50"])
            ).iloc[-1]
        )

    @staticmethod
    def ema50_cross_above_200(
        df: pd.DataFrame,
    ) -> bool:

        if len(df) < 2:
            return False

        return bool(
            (
                (df["EMA_50"].shift(1) <= df["EMA_200"].shift(1))
                &
                (df["EMA_50"] > df["EMA_200"])
            ).iloc[-1]
        )

    @staticmethod
    def ema20_cross_below_50(
        df: pd.DataFrame,
    ) -> bool:

        if len(df) < 2:
            return False

        return bool(
            (
                (df["EMA_20"].shift(1) >= df["EMA_50"].shift(1))
                &
                (df["EMA_20"] < df["EMA_50"])
            ).iloc[-1]
        )

    # =========================================================
    # 52 WEEK
    # =========================================================

    @staticmethod
    def near_52_week_high(
        df: pd.DataFrame,
    ) -> bool:

        if len(df) < 20:
            return False

        highest = (
            df["high"]
            .rolling(252, min_periods=20)
            .max()
            .iloc[-1]
        )

        close = df["close"].iloc[-1]

        if pd.isna(highest):
            return False

        return close >= highest * 0.95

    @staticmethod
    def breakout_52_week(
        df: pd.DataFrame,
    ) -> bool:

        if len(df) < 21:
            return False

        highest = (
            df["high"]
            .shift(1)
            .rolling(252, min_periods=20)
            .max()
            .iloc[-1]
        )

        close = df["close"].iloc[-1]

        if pd.isna(highest):
            return False

        return close > highest

    @staticmethod
    def near_52_week_low(
        df: pd.DataFrame,
    ) -> bool:

        if len(df) < 20:
            return False

        lowest = (
            df["low"]
            .rolling(252, min_periods=20)
            .min()
            .iloc[-1]
        )

        close = df["close"].iloc[-1]

        if pd.isna(lowest):
            return False

        return close <= lowest * 1.05

    # =========================================================
    # DELIVERY / LIQUIDITY
    # =========================================================

    @staticmethod
    def high_turnover(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "TURNOVER",
            )
            >= 100_000_000
        )

    @staticmethod
    def liquid_stock(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "volume",
            )
            >= 500_000
        )

    @staticmethod
    def high_delivery(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "DELIVERY_PERCENT",
            )
            >= 50
        )

    # =========================================================
    # OPTIONS / F&O
    # =========================================================

    @staticmethod
    def long_buildup(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "OI_CHANGE",
            ) > 0
            and
            ScannerRules._number(
                latest,
                "PRICE_CHANGE",
            ) > 0
        )

    @staticmethod
    def short_buildup(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "OI_CHANGE",
            ) > 0
            and
            ScannerRules._number(
                latest,
                "PRICE_CHANGE",
            ) < 0
        )

    @staticmethod
    def short_covering(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "OI_CHANGE",
            ) < 0
            and
            ScannerRules._number(
                latest,
                "PRICE_CHANGE",
            ) > 0
        )

    @staticmethod
    def long_unwinding(latest: Any) -> bool:

        return (
            ScannerRules._number(
                latest,
                "OI_CHANGE",
            ) < 0
            and
            ScannerRules._number(
                latest,
                "PRICE_CHANGE",
            ) < 0
        )

    # =========================================================
    # CORPORATE ACTIONS
    # =========================================================

    @staticmethod
    def earnings_today(f: Any) -> bool:

        return ScannerRules._bool(
            f,
            "earnings_today",
        )

    @staticmethod
    def dividend_today(f: Any) -> bool:

        return ScannerRules._bool(
            f,
            "dividend_today",
        )

    @staticmethod
    def bonus_issue(f: Any) -> bool:

        return ScannerRules._bool(
            f,
            "bonus_issue",
        )

    @staticmethod
    def split(f: Any) -> bool:

        return ScannerRules._bool(
            f,
            "stock_split",
        )

    # =========================================================
    # INSTITUTIONAL / SHAREHOLDING
    # =========================================================

    @staticmethod
    def promoter_holding(f: Any) -> bool:

        return (
            ScannerRules._number(
                f,
                "promoter_holding",
            )
            >= 50
        )

    @staticmethod
    def fii_buying(f: Any) -> bool:

        return (
            ScannerRules._number(
                f,
                "fii_change",
            )
            > 0
        )

    @staticmethod
    def dii_buying(f: Any) -> bool:

        return (
            ScannerRules._number(
                f,
                "dii_change",
            )
            > 0
        )

    # =========================================================
    # MASTER TREND FORGE FILTER
    # =========================================================

    @staticmethod
    def trendforge_buy(
        df: pd.DataFrame,
        latest: Any,
        f: Any = None,
    ) -> int:
        """
        Lightweight pre-score filter.

        This does NOT replace ScoringEngine.

        Returns:
            0 - 100
        """

        score = 0

        # -----------------------------
        # Technical
        # -----------------------------

        if ScannerRules.ema_bullish(latest):
            score += 10

        if ScannerRules.ema9_above_26(latest):
            score += 5

        if ScannerRules.vwma9_above_26(latest):
            score += 5

        if ScannerRules.breakout(latest):
            score += 10

        if ScannerRules.high_volume(latest):
            score += 10

        if ScannerRules.macd_bullish(latest):
            score += 10

        if ScannerRules.adx_strong(latest):
            score += 10

        if ScannerRules.above_vwap(latest):
            score += 5

        if ScannerRules.positive_money_flow(latest):
            score += 5

        if ScannerRules.near_52_week_high(df):
            score += 10

        # -----------------------------
        # Fundamentals
        # -----------------------------

        if f is not None:

            if ScannerRules.strong_fundamentals(f):
                score += 10

            if ScannerRules.promoter_holding(f):
                score += 5

            if ScannerRules.strong_growth(f):
                score += 5

        return min(
            score,
            100,
        )

    # =========================================================
    # UTILITY
    # =========================================================

    @staticmethod
    def latest(
        df: pd.DataFrame,
    ) -> pd.Series:

        if df is None or df.empty:
            raise ValueError(
                "Cannot extract latest row from empty DataFrame"
            )

        return df.iloc[-1]