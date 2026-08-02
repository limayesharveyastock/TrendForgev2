class RankingService:

    def rank(self, signals):

        return sorted(

            signals,

            key=lambda x: (

                x.overall_score,

                x.confidence,

                x.risk_reward

            ),

            reverse=True

        )