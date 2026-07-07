"""
trade_executor.py
-------------------------------------
TrendForge Trade Execution Engine

Supports:
- Paper Trading
- Live Trading (future)
- Buy / Sell Orders
- Risk Manager Integration
- Order History
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

from risk_manager import RiskManager, TradeRequest


# ---------------------------------------------------
# ORDER
# ---------------------------------------------------

@dataclass
class Order:

    symbol: str

    side: str

    quantity: int

    entry: float

    stoploss: float

    target: float

    status: str

    order_time: datetime


# ---------------------------------------------------
# EXECUTOR
# ---------------------------------------------------

class TradeExecutor:

    def __init__(self,
                 risk_manager: RiskManager,
                 paper_trade=True):

        self.risk_manager = risk_manager

        self.paper_trade = paper_trade

        self.orders: List[Order] = []

    # ------------------------------------------------

    def place_trade(self,
                    symbol,
                    entry,
                    stoploss,
                    target,
                    side="BUY"):

        request = TradeRequest(
            symbol=symbol,
            entry=entry,
            stoploss=stoploss,
            target=target,
            direction=side
        )

        result = self.risk_manager.validate_trade(request)

        if not result.approved:

            return {
                "success": False,
                "reason": result.reason
            }

        order = Order(
            symbol=symbol,
            side=side,
            quantity=result.quantity,
            entry=entry,
            stoploss=stoploss,
            target=target,
            status="OPEN",
            order_time=datetime.now()
        )

        if self.paper_trade:

            order.status = "PAPER"

        else:

            self.execute_live_order(order)

        self.orders.append(order)

        self.risk_manager.register_trade()

        return {
            "success": True,
            "order": order
        }

    # ------------------------------------------------

    def execute_live_order(self, order):

        """
        Replace this function with
        Zerodha Kite API order placement.
        """

        order.status = "LIVE"

    # ------------------------------------------------

    def close_trade(self,
                    symbol,
                    exit_price):

        for order in self.orders:

            if order.symbol == symbol and order.status in ["PAPER", "LIVE"]:

                if order.side == "BUY":

                    pnl = (exit_price - order.entry) * order.quantity

                else:

                    pnl = (order.entry - exit_price) * order.quantity

                order.status = "CLOSED"

                self.risk_manager.close_trade(pnl)

                return {
                    "success": True,
                    "pnl": pnl
                }

        return {
            "success": False,
            "reason": "Order not found."
        }

    # ------------------------------------------------

    def get_open_orders(self):

        return [
            order for order in self.orders
            if order.status in ["PAPER", "LIVE"]
        ]

    # ------------------------------------------------

    def get_closed_orders(self):

        return [
            order for order in self.orders
            if order.status == "CLOSED"
        ]

    # ------------------------------------------------

    def total_open_positions(self):

        return len(self.get_open_orders())