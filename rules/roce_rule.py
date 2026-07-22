from rules.base_rule import BaseRule

from models.engine_result import RuleResult

from utils.scoring import band_score


class ROCERule(BaseRule):

    def __init__(self):

        super().__init__(

            name="ROCE",

            field="roce",

            weight=8

        )

        self.bands = [

            (30,8),

            (25,7),

            (20,6),

            (15,4),

            (10,2),

            (0,0)

        ]

    def evaluate(self, stock):

        value = stock.get("roce",0)

        score = band_score(value,self.bands)

        return RuleResult(

            name=self.name,

            score=score,

            max_score=self.weight,

            passed=score>0,

            value=value,

            reason=f"ROCE : {value}%"

        )