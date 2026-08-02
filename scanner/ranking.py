class RankingEngine:

    def rank(self, signals):

        return sorted(

            signals,

            key=lambda x: (

                x.overall_score,

                x.confidence

            ),

            reverse=True

        )