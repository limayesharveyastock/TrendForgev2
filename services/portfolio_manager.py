"""
portfolio_manager.py
-------------------------------------
TrendForge Portfolio Management

Features
--------
- Holdings Management
- Open Positions
- Closed Positions
- Realized P&L
- Unrealized P&L
- Portfolio Value
- Position Summary
"""

from dataclasses import dataclass
from typing import Dict
from datetime import datetime


# -------------------------------------------------------
# POSITION
# -------------------------------------------------------

@dataclass
class Position:

    symbol: str

    quantity: int

    average_price: float

    current_price: float

    last_updated: datetime


# -------------------------------------------------------
# PORTFOLIO
# -------------------------------------------------------

class PortfolioManager:

    def __init__(self):

        self.positions: Dict[str, Position] = {}

        self.realized_pnl = 0.0

    # ---------------------------------------------------

    def add_position(
        self,
        symbol,
        quantity,
        price
    ):

        if symbol in self.positions:

            pos = self.positions[symbol]

            total_qty = pos.quantity + quantity

            avg_price = (
                (pos.average_price * pos.quantity)
                + (price * quantity)
            ) / total_qty

            pos.quantity = total_qty

            pos.average_price = avg_price

            pos.current_price = price

            pos.last_updated = datetime.now()

        else:

            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                average_price=price,
                current_price=price,
                last_updated=datetime.now()
            )

    # ---------------------------------------------------

    def reduce_position(
        self,
        symbol,
        quantity,
        sell_price
    ):

        if symbol not in self.positions:

            return 0

        pos = self.positions[symbol]

        quantity = min(quantity, pos.quantity)

        pnl = (
            sell_price - pos.average_price
        ) * quantity

        self.realized_pnl += pnl

        pos.quantity -= quantity

        pos.current_price = sell_price

        pos.last_updated = datetime.now()

        if pos.quantity == 0:

            del self.positions[symbol]

        return pnl

    # ---------------------------------------------------

    def update_market_price(
        self,
        symbol,
        market_price
    ):

        if symbol in self.positions:

            self.positions[symbol].current_price = market_price

            self.positions[symbol].last_updated = datetime.now()

    # ---------------------------------------------------

    def unrealized_pnl(self):

        total = 0

        for pos in self.positions.values():

            total += (
                pos.current_price
                - pos.average_price
            ) * pos.quantity

        return total

    # ---------------------------------------------------

    def invested_value(self):

        total = 0

        for pos in self.positions.values():

            total += (
                pos.average_price
                * pos.quantity
            )

        return total

    # ---------------------------------------------------

    def market_value(self):

        total = 0

        for pos in self.positions.values():

            total += (
                pos.current_price
                * pos.quantity
            )

        return total

    # ---------------------------------------------------

    def total_pnl(self):

        return (
            self.realized_pnl
            + self.unrealized_pnl()
        )

    # ---------------------------------------------------

    def portfolio_summary(self):

        return {

            "Total Holdings": len(self.positions),

            "Invested Value": round(
                self.invested_value(), 2
            ),

            "Market Value": round(
                self.market_value(), 2
            ),

            "Realized PnL": round(
                self.realized_pnl, 2
            ),

            "Unrealized PnL": round(
                self.unrealized_pnl(), 2
            ),

            "Total PnL": round(
                self.total_pnl(), 2
            )
        }

    # ---------------------------------------------------

    def get_positions(self):

        return list(self.positions.values())

    # ---------------------------------------------------

    def clear(self):

        self.positions.clear()

        self.realized_pnl = 0