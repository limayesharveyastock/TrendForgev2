class Rejects:

    def get(self, signals):

        return [

            s

            for s in signals

            if s.signal in (

                "SELL",

                "REDUCE"

            )

        ]