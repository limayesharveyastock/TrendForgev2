class AlertManager:

    def build(self, signal):

        return {

            "symbol": signal.symbol,

            "signal": signal.signal,

            "entry": signal.entry,

            "stoploss": signal.stoploss,

            "target1": signal.target1,

            "confidence": signal.confidence,

            "score": signal.overall_score,

        }