class EquityCurve:

    def build(self, trades):

        equity = []

        balance = 0

        for trade in trades:

            balance += trade.pnl

            equity.append(balance)

        return equity