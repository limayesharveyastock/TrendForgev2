class MaxDrawdown:

    def calculate(self, equity):

        peak = equity[0]

        max_dd = 0

        for value in equity:

            if value > peak:

                peak = value

            dd = (

                peak - value

            ) / peak if peak else 0

            max_dd = max(

                max_dd,

                dd

            )

        return round(

            max_dd * 100,

            2

        )