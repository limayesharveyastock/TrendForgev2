class RiskRewardRule:

    def calculate(

        self,

        entry,

        stop,

        multiplier=2

    ):

        risk = entry - stop

        reward = risk * multiplier

        if risk <= 0:

            return 0

        return round(

            reward / risk,

            2

        )