class StrategyRunner:

    def __init__(

        self,

        scanner,

        execution,

    ):

        self.scanner = scanner

        self.execution = execution

    def execute(self, historical_data):

        trades = []

        for candle in historical_data:

            signals = self.scanner.scan_candle(candle)

            trades.extend(

                self.execution.execute(

                    signals,

                    candle

                )

            )

        return trades