from rules.base_rule import BaseRule
from models.engine_result import RuleResult


class EMAAlignmentRule(BaseRule):

    def __init__(self):

        super().__init__(

            "EMA Alignment",

            "ema_alignment",

            10

        )

    def evaluate(self, snapshot):

        bullish = (

            snapshot.ema9 >

            snapshot.ema20 >

            snapshot.ema50 >

            snapshot.ema100 >

            snapshot.ema200

        )

        bearish = (

            snapshot.ema9 <

            snapshot.ema20 <

            snapshot.ema50 <

            snapshot.ema100 <

            snapshot.ema200

        )

        if bullish:

            return RuleResult(

                self.name,

                10,

                10,

                True,

                "Perfect bullish EMA alignment"

            )

        if bearish:

            return RuleResult(

                self.name,

                0,

                10,

                False,

                "Bearish EMA alignment"

            )

        return RuleResult(

            self.name,

            5,

            10,

            True,

            "Mixed EMA structure"

        )