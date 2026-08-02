class VolatilityRule:

    def score(self, snapshot):

        atr_percent = (

            snapshot.atr /

            snapshot.close

        ) * 100

        if atr_percent < 2:

            return 100

        if atr_percent < 3:

            return 90

        if atr_percent < 4:

            return 75

        if atr_percent < 5:

            return 60

        return 40