"""
risk_manager.py
----------------------------------
TrendForge Risk Management Engine

Responsibilities:
- Position sizing
- Risk per trade
- Capital allocation
- Daily loss protection
- Maximum open positions
- Reward : Risk validation
- Trade approval / rejection
"""

from dataclasses import dataclass
from datetime import datetime


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

@dataclass
class RiskConfig:
    capital: float = 100000

    risk_per_trade_percent: float = 1.0

    max_daily_loss_percent: float = 3.0

    max_open_positions: int = 5

    max_capital_per_trade_percent: float = 20.0

    minimum_rr: float = 2.0


# ---------------------------------------------------------
# TRADE INPUT
# ---------------------------------------------------------

@dataclass
class TradeRequest:

    symbol: str

    entry: float

    stoploss: float

    target: float

    direction: str = "BUY"


# ---------------------------------------------------------
# RESULT
# ---------------------------------------------------------

@dataclass
class RiskResult:

    approved: bool

    quantity: int

    risk_amount: float

    reward_risk: float

    reason: str = ""


# ---------------------------------------------------------
# ENGINE
# ---------------------------------------------------------

class RiskManager:

    def __init__(self, config: RiskConfig):

        self.config = config

        self.today_loss = 0

        self.open_positions = 0

        self.last_reset = datetime.now().date()

    # -------------------------------------------------

    def reset_daily(self):

        today = datetime.now().date()

        if today != self.last_reset:

            self.today_loss = 0

            self.last_reset = today

    # -------------------------------------------------

    def calculate_position_size(self, entry, stoploss):

        risk_amount = (
            self.config.capital
            * self.config.risk_per_trade_percent
            / 100
        )

        risk_per_share = abs(entry - stoploss)

        if risk_per_share <= 0:

            return 0, risk_amount

        qty = int(risk_amount / risk_per_share)

        max_trade_value = (
            self.config.capital
            * self.config.max_capital_per_trade_percent
            / 100
        )

        max_qty = int(max_trade_value / entry)

        qty = min(qty, max_qty)

        return qty, risk_amount

    # -------------------------------------------------

    def reward_risk(self, entry, stoploss, target):

        reward = abs(target - entry)

        risk = abs(entry - stoploss)

        if risk == 0:

            return 0

        return reward / risk

    # -------------------------------------------------

    def validate_trade(self, trade: TradeRequest):

        self.reset_daily()

        if self.today_loss >= (
            self.config.capital
            * self.config.max_daily_loss_percent
            / 100
        ):

            return RiskResult(
                False,
                0,
                0,
                0,
                "Maximum daily loss reached."
            )

        if self.open_positions >= self.config.max_open_positions:

            return RiskResult(
                False,
                0,
                0,
                0,
                "Maximum open positions reached."
            )

        rr = self.reward_risk(
            trade.entry,
            trade.stoploss,
            trade.target
        )

        if rr < self.config.minimum_rr:

            return RiskResult(
                False,
                0,
                0,
                rr,
                "Reward/Risk too low."
            )

        qty, risk_amount = self.calculate_position_size(
            trade.entry,
            trade.stoploss
        )

        if qty <= 0:

            return RiskResult(
                False,
                0,
                risk_amount,
                rr,
                "Position size is zero."
            )

        return RiskResult(
            True,
            qty,
            risk_amount,
            rr,
            "Trade Approved"
        )

    # -------------------------------------------------

    def register_trade(self):

        self.open_positions += 1

    # -------------------------------------------------

    def close_trade(self, pnl):

        self.open_positions = max(0, self.open_positions - 1)

        if pnl < 0:

            self.today_loss += abs(pnl)

    # -------------------------------------------------

    def remaining_daily_loss(self):

        limit = (
            self.config.capital
            * self.config.max_daily_loss_percent
            / 100
        )

        return max(0, limit - self.today_loss)