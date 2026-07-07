"""
TrendForge v2
Scanner Rules Engine
"""

from __future__ import annotations

import pandas as pd


class ScannerRules:

    # =====================================================
    # TREND
    # =====================================================

    @staticmethod
    def ema_bullish(latest):

        return (
            latest["EMA_20"] >
            latest["EMA_50"] >
            latest["EMA_200"]
        )

    @staticmethod
    def ema_bearish(latest):

        return (
            latest["EMA_20"] <
            latest["EMA_50"] <
            latest["EMA_200"]
        )

    @staticmethod
    def golden_cross(latest):

        return (
            latest["EMA_50"] >
            latest["EMA_200"]
        )

    @staticmethod
    def death_cross(latest):

        return (
            latest["EMA_50"] <
            latest["EMA_200"]
        )

    # =====================================================
    # MOMENTUM
    # =====================================================

    @staticmethod
    def rsi_bullish(latest):

        return 55 <= latest["RSI"] <= 70

    @staticmethod
    def rsi_oversold(latest):

        return latest["RSI"] < 30

    @staticmethod
    def rsi_overbought(latest):

        return latest["RSI"] > 70

    @staticmethod
    def macd_bullish(latest):

        return (
            latest["MACD"] >
            latest["MACD_SIGNAL"]
        )

    @staticmethod
    def adx_strong(latest):

        return latest["ADX"] > 25

    # =====================================================
    # VOLUME
    # =====================================================

    @staticmethod
    def high_volume(latest):

        return latest["RVOL"] >= 2

    @staticmethod
    def medium_volume(latest):

        return latest["RVOL"] >= 1.5

    @staticmethod
    def positive_money_flow(latest):

        return latest["CMF"] > 0

    @staticmethod
    def above_vwap(latest):

        return latest["close"] > latest["VWAP"]

    # =====================================================
    # VOLATILITY
    # =====================================================

    @staticmethod
    def atr_expansion(latest):

        return latest["ATR_PERCENT"] > 2

    @staticmethod
    def bb_squeeze(latest):

        return latest["BB_WIDTH"] < 0.08

    # =====================================================
    # PRICE ACTION
    # =====================================================

    @staticmethod
    def breakout(latest):

        return latest["BREAKOUT"]

    @staticmethod
    def breakdown(latest):

        return latest["BREAKDOWN"]

    @staticmethod
    def gap_up(latest):

        return latest["GAP_UP"]

    @staticmethod
    def gap_down(latest):

        return latest["GAP_DOWN"]

    @staticmethod
    def uptrend(latest):

        return latest["UPTREND"]

    @staticmethod
    def downtrend(latest):

        return latest["DOWNTREND"]

    @staticmethod
    def inside_bar(latest):

        return latest["INSIDE_BAR"]

    @staticmethod
    def nr7(latest):

        return latest["NR7"]

    # =====================================================
    # CANDLESTICK
    # =====================================================

    @staticmethod
    def bullish_engulfing(latest):

        return latest["BULLISH_ENGULFING"]

    @staticmethod
    def bearish_engulfing(latest):

        return latest["BEARISH_ENGULFING"]

    @staticmethod
    def hammer(latest):

        return latest["HAMMER"]

    @staticmethod
    def doji(latest):

        return latest["DOJI"]

    # =====================================================
    # FUNDAMENTALS
    # =====================================================

    @staticmethod
    def strong_fundamentals(f):

        return (

            f.roe >= 15

            and

            f.roce >= 15

            and

            f.debt_to_equity < 0.5

            and

            f.sales_growth > 10

            and

            f.profit_growth > 10

        )

    @staticmethod
    def value_stock(f):

        return (

            0 < f.pe < 25

            and

            f.pb < 5

        )

    @staticmethod
    def quality_stock(f):

        return (

            f.roe > 20

            and

            f.roce > 20

        )

    # =====================================================
    # COMBINATIONS
    # =====================================================

    @staticmethod
    def breakout_buy(latest):

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
    def swing_buy(latest):

        return (

            ScannerRules.uptrend(latest)

            and

            ScannerRules.rsi_bullish(latest)

            and

            ScannerRules.medium_volume(latest)

        )

    @staticmethod
    def intraday_buy(latest):

        return (

            ScannerRules.above_vwap(latest)

            and

            ScannerRules.high_volume(latest)

            and

            ScannerRules.macd_bullish(latest)

        )

    @staticmethod
    def reversal_buy(latest):

        return (

            ScannerRules.rsi_oversold(latest)

            and

            ScannerRules.hammer(latest)

        )

    @staticmethod
    def positional_buy(latest):

        return (

            ScannerRules.ema_bullish(latest)

            and

            ScannerRules.breakout(latest)

            and

            ScannerRules.adx_strong(latest)

        )

    # =====================================================
    # UTILITIES
    # =====================================================

    @staticmethod
    def latest(df: pd.DataFrame):

        return df.iloc[-1]

            # =====================================================
    # EMA CROSSOVERS
    # =====================================================

    @staticmethod
    def ema20_cross_above_50(df):

        return (

            (df["EMA_20"].shift(1) <= df["EMA_50"].shift(1))

            &

            (df["EMA_20"] > df["EMA_50"])

        ).iloc[-1]

    @staticmethod
    def ema50_cross_above_200(df):

        return (

            (df["EMA_50"].shift(1) <= df["EMA_200"].shift(1))

            &

            (df["EMA_50"] > df["EMA_200"])

        ).iloc[-1]

    @staticmethod
    def ema20_cross_below_50(df):

        return (

            (df["EMA_20"].shift(1) >= df["EMA_50"].shift(1))

            &

            (df["EMA_20"] < df["EMA_50"])

        ).iloc[-1]

    # =====================================================
    # 52 WEEK
    # =====================================================

    @staticmethod
    def near_52_week_high(df):

        highest = df["high"].rolling(252).max().iloc[-1]

        close = df["close"].iloc[-1]

        return close >= highest * 0.95

    @staticmethod
    def breakout_52_week(df):

        highest = df["high"].shift(1).rolling(252).max().iloc[-1]

        return df["close"].iloc[-1] > highest

    @staticmethod
    def near_52_week_low(df):

        lowest = df["low"].rolling(252).min().iloc[-1]

        return df["close"].iloc[-1] <= lowest * 1.05

    # =====================================================
    # DELIVERY & LIQUIDITY
    # =====================================================

    @staticmethod
    def high_turnover(latest):

        return latest.get("TURNOVER", 0) >= 10_00_00_000

    @staticmethod
    def liquid_stock(latest):

        return latest["volume"] >= 500000

    @staticmethod
    def high_delivery(latest):

        return latest.get("DELIVERY_PERCENT", 0) >= 50

    # =====================================================
    # OPTIONS
    # =====================================================

    @staticmethod
    def long_buildup(latest):

        return (

            latest.get("OI_CHANGE", 0) > 0

            and

            latest.get("PRICE_CHANGE", 0) > 0

        )

    @staticmethod
    def short_buildup(latest):

        return (

            latest.get("OI_CHANGE", 0) > 0

            and

            latest.get("PRICE_CHANGE", 0) < 0

        )

    @staticmethod
    def short_covering(latest):

        return (

            latest.get("OI_CHANGE", 0) < 0

            and

            latest.get("PRICE_CHANGE", 0) > 0

        )

    @staticmethod
    def long_unwinding(latest):

        return (

            latest.get("OI_CHANGE", 0) < 0

            and

            latest.get("PRICE_CHANGE", 0) < 0

        )

    # =====================================================
    # CORPORATE ACTIONS
    # =====================================================

    @staticmethod
    def earnings_today(f):

        return getattr(f, "earnings_today", False)

    @staticmethod
    def dividend_today(f):

        return getattr(f, "dividend_today", False)

    @staticmethod
    def bonus_issue(f):

        return getattr(f, "bonus_issue", False)

    @staticmethod
    def split(f):

        return getattr(f, "stock_split", False)

    # =====================================================
    # GROWTH
    # =====================================================

    @staticmethod
    def strong_growth(f):

        return (

            f.sales_growth >= 20

            and

            f.profit_growth >= 20

        )

    @staticmethod
    def multibagger_filter(f):

        return (

            f.roe >= 20

            and

            f.roce >= 20

            and

            f.debt_to_equity <= 0.30

            and

            f.sales_growth >= 15

            and

            f.profit_growth >= 15

        )

    # =====================================================
    # INSTITUTIONAL QUALITY
    # =====================================================

    @staticmethod
    def promoter_holding(f):

        return f.promoter_holding >= 50

    @staticmethod
    def fii_buying(f):

        return getattr(f, "fii_change", 0) > 0

    @staticmethod
    def dii_buying(f):

        return getattr(f, "dii_change", 0) > 0

    # =====================================================
    # MASTER RULE
    # =====================================================

    @staticmethod
    def trendforge_buy(df, latest, f=None):

        score = 0

        if ScannerRules.ema_bullish(latest):
            score += 10

        if ScannerRules.breakout(latest):
            score += 10

        if ScannerRules.high_volume(latest):
            score += 10

        if ScannerRules.macd_bullish(latest):
            score += 10

        if ScannerRules.adx_strong(latest):
            score += 10

        if ScannerRules.near_52_week_high(df):
            score += 10

        if f:

            if ScannerRules.strong_fundamentals(f):
                score += 20

            if ScannerRules.promoter_holding(f):
                score += 10

            if ScannerRules.strong_growth(f):
                score += 10

        return score