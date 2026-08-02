class ScannerReport:

    def summary(self, signals):

        return {

            "total": len(signals),

            "strong_buy": len(

                [

                    s

                    for s in signals

                    if s.signal == "STRONG BUY"

                ]

            ),

            "buy": len(

                [

                    s

                    for s in signals

                    if s.signal == "BUY"

                ]

            ),

            "watchlist": len(

                [

                    s

                    for s in signals

                    if s.signal == "WATCHLIST"

                ]

            ),

            "sell": len(

                [

                    s

                    for s in signals

                    if s.signal == "SELL"

                ]

            )

        }