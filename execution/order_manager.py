from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Order:

    symbol: str

    side: str

    quantity: int

    price: float

    stoploss: float

    target1: float

    target2: float

    target3: float

    strategy: str

    timestamp: datetime


class OrderManager:

    def create(self, signal):

        return Order(

            symbol=signal.symbol,

            side=signal.signal,

            quantity=signal.quantity,

            price=signal.entry,

            stoploss=signal.stoploss,

            target1=signal.target1,

            target2=signal.target2,

            target3=signal.target3,

            strategy=signal.strategy,

            timestamp=datetime.now()

        )