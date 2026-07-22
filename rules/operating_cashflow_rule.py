from rules.base_rule import BaseRule
from models.engine_result import RuleResult


class OperatingCashFlowRule(BaseRule):

    def __init__(self):

        super().__init__(

            "Operating Cash Flow",

            "operating_cashflow",

            6

        )

    def evaluate(self,stock):

        cash=stock.get("operating_cashflow",0)

        if cash>0:

            score=6

        else:

            score=0

        return RuleResult(

            name=self.name,

            score=score,

            max_score=6,

            passed=score==6,

            value=cash,

            reason=f"Operating Cash Flow : {cash}"

        )