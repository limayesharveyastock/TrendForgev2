class RiskRewardRule:

    def evaluate(self, signal):

        risk = signal.entry - signal.stoploss

        reward = signal.target2 - signal.entry

        if risk <= 0:

            return 0

        return reward / risk