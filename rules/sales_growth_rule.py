from rules.base_rule import BaseRule
from models.engine_result import RuleResult
from utils.scoring import band_score


class SalesGrowthRule(BaseRule):

    def __init__(self):
        super().__init__(
            name="Sales Growth",
            field="sales_growth",
            weight=7
        )

        self.bands = [
            (30, 7),
            (25, 6),
            (20, 5),
            (15, 4),
            (10, 2),
            (0, 0)
        ]

    def evaluate(self, stock):

        value = stock.get("sales_growth", 0)

        score = band_score(value, self.bands)

        return RuleResult(
            name=self.name,
            score=score,
            max_score=self.weight,
            passed=score >= 4,
            value=value,
            reason=f"Sales Growth : {value:.2f}%"
        )