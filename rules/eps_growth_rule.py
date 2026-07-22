from rules.base_rule import BaseRule
from models.engine_result import RuleResult
from utils.scoring import band_score


class EPSGrowthRule(BaseRule):

    def __init__(self):

        super().__init__(
            "EPS Growth",
            "eps_growth",
            6
        )

        self.bands=[

            (30,6),

            (25,5),

            (20,4),

            (15,3),

            (10,2),

            (0,0)

        ]

    def evaluate(self,stock):

        value=stock.get("eps_growth",0)

        score=band_score(value,self.bands)

        return RuleResult(

            name=self.name,

            score=score,

            max_score=self.weight,

            passed=score>=3,

            value=value,

            reason=f"EPS Growth : {value:.2f}%"

        )
        