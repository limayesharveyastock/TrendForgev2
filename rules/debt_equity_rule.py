from rules.base_rule import BaseRule
from models.engine_result import RuleResult


class DebtEquityRule(BaseRule):

    def __init__(self):

        super().__init__(

            "Debt Equity",

            "debt_equity",

            8

        )

    def evaluate(self,stock):

        debt=stock.get("debt_equity",999)

        if debt<=0.25:

            score=8

        elif debt<=0.50:

            score=7

        elif debt<=1:

            score=5

        elif debt<=2:

            score=2

        else:

            score=0

        return RuleResult(

            name=self.name,

            score=score,

            max_score=8,

            passed=score>=5,

            value=debt,

            reason=f"Debt/Equity : {debt}"

        )