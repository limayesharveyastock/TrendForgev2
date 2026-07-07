"""
performance_analytics.py
--------------------------------------------------
TrendForge Performance Analytics Engine

Features
--------
- Total Trades
- Winning Trades
- Losing Trades
- Win Rate
- Gross Profit
- Gross Loss
- Net Profit
- Profit Factor
- Average Winner
- Average Loser
- Expectancy
- Maximum Drawdown
- Equity Curve
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


# --------------------------------------------------
# TRADE RECORD
# --------------------------------------------------

@dataclass
class TradeRecord:

    symbol: str

    entry: float

    exit: float

    quantity: int

    pnl: float

    side: str

    open_time: datetime

    close_time: datetime


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

class PerformanceAnalytics:

    def __init__(self):

        self.trades: List[TradeRecord] = []

    # ----------------------------------------------

    def add_trade(self, trade: TradeRecord):

        self.trades.append(trade)

    # ----------------------------------------------

    def total_trades(self):

        return len(self.trades)

    # ----------------------------------------------

    def winning_trades(self):

        return len(
            [t for t in self.trades if t.pnl > 0]
        )

    # ----------------------------------------------

    def losing_trades(self):

        return len(
            [t for t in self.trades if t.pnl < 0]
        )

    # ----------------------------------------------

    def breakeven_trades(self):

        return len(
            [t for t in self.trades if t.pnl == 0]
        )

    # ----------------------------------------------

    def win_rate(self):

        total = self.total_trades()

        if total == 0:

            return 0

        return round(
            self.winning_trades() * 100 / total,
            2
        )

    # ----------------------------------------------

    def gross_profit(self):

        return sum(
            t.pnl for t in self.trades
            if t.pnl > 0
        )

    # ----------------------------------------------

    def gross_loss(self):

        return abs(sum(
            t.pnl for t in self.trades
            if t.pnl < 0
        ))

    # ----------------------------------------------

    def net_profit(self):

        return sum(
            t.pnl for t in self.trades
        )

    # ----------------------------------------------

    def profit_factor(self):

        loss = self.gross_loss()

        if loss == 0:

            return float("inf")

        return round(
            self.gross_profit() / loss,
            2
        )

    # ----------------------------------------------

    def average_winner(self):

        winners = [
            t.pnl
            for t in self.trades
            if t.pnl > 0
        ]

        if not winners:

            return 0

        return round(
            sum(winners) / len(winners),
            2
        )

    # ----------------------------------------------

    def average_loser(self):

        losers = [
            abs(t.pnl)
            for t in self.trades
            if t.pnl < 0
        ]

        if not losers:

            return 0

        return round(
            sum(losers) / len(losers),
            2
        )

    # ----------------------------------------------

    def expectancy(self):

        if self.total_trades() == 0:

            return 0

        win_prob = self.winning_trades() / self.total_trades()

        loss_prob = self.losing_trades() / self.total_trades()

        expectancy = (
            win_prob * self.average_winner()
            -
            loss_prob * self.average_loser()
        )

        return round(expectancy, 2)

    # ----------------------------------------------

    def equity_curve(self):

        curve = []

        equity = 0

        for trade in self.trades:

            equity += trade.pnl

            curve.append(equity)

        return curve

    # ----------------------------------------------

    def maximum_drawdown(self):

        curve = self.equity_curve()

        if not curve:

            return 0

        peak = curve[0]

        max_dd = 0

        for value in curve:

            peak = max(peak, value)

            drawdown = peak - value

            max_dd = max(max_dd, drawdown)

        return round(max_dd, 2)

    # ----------------------------------------------

    def report(self):

        return {

            "Total Trades": self.total_trades(),

            "Winning Trades": self.winning_trades(),

            "Losing Trades": self.losing_trades(),

            "Breakeven Trades": self.breakeven_trades(),

            "Win Rate (%)": self.win_rate(),

            "Gross Profit": round(self.gross_profit(), 2),

            "Gross Loss": round(self.gross_loss(), 2),

            "Net Profit": round(self.net_profit(), 2),

            "Profit Factor": self.profit_factor(),

            "Average Winner": self.average_winner(),

            "Average Loser": self.average_loser(),

            "Expectancy": self.expectancy(),

            "Maximum Drawdown": self.maximum_drawdown()
        }