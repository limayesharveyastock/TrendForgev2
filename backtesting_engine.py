"""
backtesting_engine.py
------------------------------------------------------------
TrendForge Backtesting Engine

Features
--------
- Historical Strategy Testing
- BUY / SELL Simulation
- Capital Tracking
- Position Management
- Trade Log
- Equity Curve
- Performance Metrics
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from performance_analytics import (
    PerformanceAnalytics,
    TradeRecord,
)

from strategy_engine import (
    StrategyEngine,
    IndicatorSignal,
)


# ==========================================================
# PRICE BAR
# ==========================================================

@dataclass
class PriceBar:

    date: datetime

    open: float

    high: float

    low: float

    close: float

    volume: float


# ==========================================================
# POSITION
# ==========================================================

@dataclass
class BacktestPosition:

    entry_price: float

    quantity: int

    entry_time: datetime


# ==========================================================
# ENGINE
# ==========================================================

class BacktestingEngine:

    def __init__(self,
                 capital=100000):

        self.initial_capital = capital

        self.cash = capital

        self.position: Optional[
            BacktestPosition
        ] = None

        self.analytics = PerformanceAnalytics()

        self.strategy = StrategyEngine()

        self.equity_curve = []

    # ------------------------------------------------------

    def current_equity(self, market_price):

        if self.position is None:

            return self.cash

        return (
            self.cash +
            self.position.quantity * market_price
        )

    # ------------------------------------------------------

    def buy(self,
            price,
            date):

        if self.position is not None:

            return

        qty = int(self.cash / price)

        if qty <= 0:

            return

        self.cash -= qty * price

        self.position = BacktestPosition(
            entry_price=price,
            quantity=qty,
            entry_time=date
        )

    # ------------------------------------------------------

    def sell(
        self,
        price,
        date,
        symbol="UNKNOWN"
    ):

        if self.position is None:

            return

        pnl = (
            price -
            self.position.entry_price
        ) * self.position.quantity

        self.cash += (
            self.position.quantity * price
        )

        self.analytics.add_trade(

            TradeRecord(

                symbol=symbol,

                entry=self.position.entry_price,

                exit=price,

                quantity=self.position.quantity,

                pnl=pnl,

                side="BUY",

                open_time=self.position.entry_time,

                close_time=date

            )

        )

        self.position = None

    # ------------------------------------------------------

    def run(
        self,
        symbol,
        price_data: List[PriceBar],
        signal_provider
    ):

        """
        signal_provider(bar)
        must return

        List[IndicatorSignal]
        """

        for bar in price_data:

            signals = signal_provider(bar)

            result = self.strategy.evaluate(
                symbol,
                signals
            )

            if result.action == "BUY":

                self.buy(
                    bar.close,
                    bar.date
                )

            elif result.action == "SELL":

                self.sell(
                    bar.close,
                    bar.date,
                    symbol
                )

            equity = self.current_equity(
                bar.close
            )

            self.equity_curve.append(
                equity
            )

        if self.position:

            self.sell(
                price_data[-1].close,
                price_data[-1].date,
                symbol
            )

    # ------------------------------------------------------

    def final_report(self):

        report = self.analytics.report()

        report["Initial Capital"] = round(
            self.initial_capital,
            2
        )

        report["Final Capital"] = round(
            self.cash,
            2
        )

        report["Return (%)"] = round(

            (
                (
                    self.cash
                    - self.initial_capital
                )
                /
                self.initial_capital
            ) * 100,

            2

        )

        report["Equity Curve"] = self.equity_curve

        return report