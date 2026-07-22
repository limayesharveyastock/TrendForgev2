from rules.base_rule import BaseRule
from models.engine_result import RuleResult


class CurrentRatioRule(BaseRule):

    def __init__(self):

        super().__init__(

            "Current Ratio",

            "current_ratio",

            4

        )

    def evaluate(self,stock):

        ratio=stock.get("current_ratio",0)

        if ratio>=2:

            score=4

        elif ratio>=1.5:

            score=3

        elif ratio>=1:

            score=2

        else:

            score=0

        return RuleResult(

            name=self.name,

            score=score,

            max_score=4,

            passed=score>=2,

            value=ratio,

            reason=f"Current Ratio : {ratio}"

        )
    