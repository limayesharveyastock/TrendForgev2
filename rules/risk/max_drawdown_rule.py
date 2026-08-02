class MaxDrawdownRule:

    MAX_DRAWDOWN = 10

    def evaluate(

        self,

        drawdown

    ):

        return drawdown <= self.MAX_DRAWDOWN