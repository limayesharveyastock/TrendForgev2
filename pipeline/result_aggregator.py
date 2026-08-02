class ResultAggregator:

    def aggregate(

        self,

        results,

    ):

        total = 0

        confidence = 0

        reasons = []

        for result in results.values():

            total += result.score

            confidence += result.confidence

            reasons.extend(result.reasons)

        return {

            "score": total,

            "confidence": confidence / len(results),

            "reasons": reasons[:20],

        }