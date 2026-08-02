import statistics
import math


class SharpeRatio:

    def calculate(

        self,

        returns,

        risk_free=0.06

    ):

        if len(returns) < 2:

            return 0

        excess = [

            r - risk_free/252

            for r in returns

        ]

        return (

            statistics.mean(excess)

            /

            statistics.stdev(excess)

        ) * math.sqrt(252)