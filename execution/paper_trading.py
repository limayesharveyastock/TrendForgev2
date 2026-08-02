from backtest.trade import Trade


class PaperTrading:

    def execute(self, order, candle):

        pnl = (

            candle.close -

            order.price

        ) * order.quantity

        return Trade(

            symbol=order.symbol,

            entry_date=order.timestamp,

            exit_date=candle.timestamp,

            entry_price=order.price,

            exit_price=candle.close,

            quantity=order.quantity,

            side=order.side,

            pnl=pnl,

            pnl_percent=(

                pnl /

                (order.price * order.quantity)

            ) * 100,

            stoploss=order.stoploss,

            target=order.target2,

            strategy=order.strategy

        )