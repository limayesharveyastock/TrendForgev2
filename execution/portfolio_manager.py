from dataclasses import dataclass, field


@dataclass(slots=True)
class Position:

    symbol: str

    quantity: int

    average_price: float

    ltp: float

    pnl: float = 0

    pnl_percent: float = 0


class PortfolioManager:

    def __init__(self):

        self.positions = {}

    def add(self, trade):

        self.positions[trade.symbol] = Position(

            symbol=trade.symbol,

            quantity=trade.quantity,

            average_price=trade.entry_price,

            ltp=trade.entry_price

        )

    def update(self, symbol, ltp):

        if symbol not in self.positions:

            return

        p = self.positions[symbol]

        p.ltp = ltp

        p.pnl = (

            ltp -

            p.average_price

        ) * p.quantity

        p.pnl_percent = (

            (

                ltp -

                p.average_price

            )

            /

            p.average_price

        ) * 100

    def total_pnl(self):

        return sum(

            p.pnl

            for p in self.positions.values()

        )