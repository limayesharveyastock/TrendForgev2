class Grade:

    @staticmethod
    def from_score(score):

        if score >= 95:

            return "S"

        if score >= 90:

            return "A+"

        if score >= 85:

            return "A"

        if score >= 80:

            return "B"

        if score >= 70:

            return "C"

        return "D"