class WatchlistEngine:

    def build(self, signals):

        return [

            s

            for s in signals

            if s.signal in (

                "BUY",

                "STRONG BUY",

                "ACCUMULATE"

            )

        ]