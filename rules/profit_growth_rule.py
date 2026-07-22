from rules.base_rule import BaseRule
from models.engine_result import RuleResult
from utils.scoring import band_score


class ProfitGrowthRule(BaseRule):

    def __init__(self):

        super().__init__(
            "Profit Growth",
            "profit_growth",
            7
        )

        self.bands = [

            (30,7),

            (25,6),

            (20,5),

            (15,4),

            (10,2),

            (0,0)

        ]

    def evaluate(self, stock):

        value = stock.get("profit_growth",0)

        score = band_score(value,self.bands)

        return RuleResult(

            name=self.name,

            score=score,

            max_score=self.weight,

            passed=score>=4,

            value=value,

            reason=f"Profit Growth : {value:.2f}%"

        )