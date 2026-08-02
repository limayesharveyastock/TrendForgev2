class ConfidenceRule:

    def calculate(self,*engines):

        confidence = sum(e.confidence for e in engines)

        return confidence / len(engines)