class PortfolioExposureRule:

    MAX_EXPOSURE = 25

    def evaluate(

        self,

        exposure

    ):

        return exposure <= self.MAX_EXPOSURE