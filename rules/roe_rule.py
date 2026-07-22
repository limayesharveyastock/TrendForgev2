from rules.base_rule import BaseRule

from models.engine_result import RuleResult

from utils.scoring import band_score


class ROERule(BaseRule):

    def __init__(self):

        super().__init__(

            "ROE",

            "roe",

            6

        )

        self.bands=[

            (20,6),

            (15,5),

            (10,3),

            (0,0)

        ]

    def evaluate(self,stock):

        value=stock.get("roe",0)

        score=band_score(value,self.bands)

        return RuleResult(

            name=self.name,

            score=score,

            max_score=self.weight,

            passed=score>0,

            value=value,

            reason=f"ROE : {value}%"

        )