class TrailingStopManager:

    def update(

        self,

        position,

        atr

    ):

        new_stop = (

            position.ltp -

            atr * 2

        )

        if new_stop > position.stoploss:

            position.stoploss = new_stop

        return position.stoploss