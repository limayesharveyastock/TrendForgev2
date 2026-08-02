from engines.base_engine import BaseEngine

from models.risk_score import RiskScore

from rules.risk.atr_stop_rule import ATRStopRule
from rules.risk.position_size_rule import PositionSizeRule
from rules.risk.risk_reward_rule import RiskRewardRule
from rules.risk.volatility_rule import VolatilityRule


class RiskEngine(BaseEngine):

    NAME = "Risk Engine"

    priority = 7

    mandatory = True

    def __init__(self):

        self.atr = ATRStopRule()

        self.position = PositionSizeRule()

        self.rr = RiskRewardRule()

        self.volatility = VolatilityRule()

    def evaluate(self, snapshot, capital):

        stop = self.atr.calculate(snapshot)

        rr = self.rr.calculate(snapshot.close, stop)

        qty = self.position.calculate(

            capital,

            1,

            snapshot.close,

            stop

        )

        score = self.volatility.score(snapshot)

        return RiskScore(

            score=score,

            confidence=95,

            stoploss=stop,

            target1=snapshot.close + (snapshot.close-stop),

            target2=snapshot.close + 2*(snapshot.close-stop),

            target3=snapshot.close + 3*(snapshot.close-stop),

            rr=rr,

            quantity=qty,

            warnings=[],

            reasons=["ATR based risk"]

        )