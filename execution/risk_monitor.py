class RiskMonitor:

    MAX_OPEN_POSITIONS = 10

    MAX_CAPITAL_USAGE = 0.80

    def validate(

        self,

        portfolio,

        capital_used,

        total_capital,

    ):

        if len(portfolio.positions) >= self.MAX_OPEN_POSITIONS:

            return False

        if (

            capital_used /

            total_capital

        ) > self.MAX_CAPITAL_USAGE:

            return False

        return True