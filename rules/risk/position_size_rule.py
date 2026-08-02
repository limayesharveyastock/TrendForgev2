class PositionSizeRule:

    def calculate(

        self,

        capital,

        risk_percent,

        entry,

        stop

    ):

        risk_amount = capital * risk_percent / 100

        per_share = abs(entry-stop)

        if per_share == 0:

            return 0

        return int(

            risk_amount /

            per_share

        )