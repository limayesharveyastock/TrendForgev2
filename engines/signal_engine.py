from engines.base_engine import BaseEngine

from config.signal_weights import SIGNAL_WEIGHTS

from models.signal import Signal


class SignalEngine(BaseEngine):

    NAME = "Signal Engine"

    priority = 100

    mandatory = True

    def generate(

        self,

        symbol,

        market,

        sector,

        fundamental,

        corporate,

        shark,

        technical,

        price_action,

        risk,

    ):

        score = (

            market.score * SIGNAL_WEIGHTS["market"]

            + sector.score * SIGNAL_WEIGHTS["sector"]

            + fundamental.score * SIGNAL_WEIGHTS["fundamental"]

            + corporate.score * SIGNAL_WEIGHTS["corporate"]

            + shark.score * SIGNAL_WEIGHTS["big_shark"]

            + technical.score * SIGNAL_WEIGHTS["technical"]

            + price_action.score * SIGNAL_WEIGHTS["price_action"]

            + risk.score * SIGNAL_WEIGHTS["risk"]

        )

        confidence = sum(

            [

                market.confidence,

                sector.confidence,

                fundamental.confidence,

                corporate.confidence,

                shark.confidence,

                technical.confidence,

                price_action.confidence,

                risk.confidence,

            ]

        ) / 8

        signal = self._classify(score)

        return Signal(

            symbol=symbol,

            signal=signal,

            confidence=round(confidence,2),

            overall_score=round(score,2),

            entry=price_action.entry,

            stoploss=risk.stoploss,

            target1=risk.target1,

            target2=risk.target2,

            target3=risk.target3,

            risk_reward=risk.rr,

            reasons=self._reasons(

                market,

                sector,

                fundamental,

                corporate,

                shark,

                technical,

                price_action,

            ),

            warnings=risk.warnings

        )

    def _classify(self, score):

        if score >= 95:

            return "STRONG BUY"

        if score >= 90:

            return "BUY"

        if score >= 85:

            return "ACCUMULATE"

        if score >= 75:

            return "WATCHLIST"

        if score >= 60:

            return "HOLD"

        if score >= 40:

            return "REDUCE"

        return "SELL"

    def _reasons(self,*engines):

        reasons=[]

        for e in engines:

            reasons.extend(e.reasons)

        return reasons[:10]