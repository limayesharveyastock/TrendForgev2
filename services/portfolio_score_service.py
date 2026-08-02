class PortfolioScoreService:

    def score(self, positions):

        if not positions:

            return 0

        total = sum(

            p.pnl_percent

            for p in positions

        )

        return round(

            total / len(positions),

            2

        )