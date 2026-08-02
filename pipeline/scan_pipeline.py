class ScanPipeline:

    def __init__(

        self,

        scanner,

        ranking,

        dashboard,

    ):

        self.scanner = scanner

        self.ranking = ranking

        self.dashboard = dashboard

    def run(

        self,

        symbols,

        capital,

    ):

        signals = self.scanner.scan(

            symbols,

            capital,

        )

        ranked = self.ranking.rank(

            signals

        )

        summary = self.dashboard.build(

            ranked

        )

        return ranked, summary