class ConfidenceCalculator:

    @staticmethod
    def calculate(results):

        if not results:

            return 0

        return round(

            sum(

                r.confidence

                for r in results

            )

            /

            len(results),

            2

        )