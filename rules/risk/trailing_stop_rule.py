class TrailingStopRule:

    def calculate(

        self,

        highest_price,

        atr

    ):

        return round(

            highest_price -

            (atr * 2),

            2

        )