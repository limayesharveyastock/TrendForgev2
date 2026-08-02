class DashboardService:

    def build(self, signals):

        return {

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

            "average_score": round(

                sum(

                    s.overall_score

                    for s in signals

                ) / len(signals),

                2

            ) if signals else 0

        }