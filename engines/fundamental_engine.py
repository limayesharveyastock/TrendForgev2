from engines.base_engine import BaseEngine, EngineResult
from config.fundamental_config import FUNDAMENTAL_CONFIG


class FundamentalEngine(BaseEngine):

    def __init__(self):
        self.cfg = FUNDAMENTAL_CONFIG

    def evaluate(self, stock):

        score = 0

        reasons = []

        warnings = []

        metrics = {}

        # -----------------------
        # ROCE
        # -----------------------

        roce = stock.get("roce", 0)

        metrics["roce"] = roce

        if roce >= 30:
            score += 8
            reasons.append("Excellent ROCE")

        elif roce >= 25:
            score += 7

        elif roce >= 20:
            score += 6

        elif roce >= 15:
            score += 4

        else:
            warnings.append("Low ROCE")

        # -----------------------
        # ROE
        # -----------------------

        roe = stock.get("roe", 0)

        metrics["roe"] = roe

        if roe >= 20:
            score += 6

        elif roe >= 15:
            score += 5

        elif roe >= 10:
            score += 3

        else:
            warnings.append("Low ROE")

        # -----------------------
        # Sales Growth
        # -----------------------

        sales = stock.get("sales_growth", 0)

        metrics["sales_growth"] = sales

        if sales >= 25:
            score += 7

        elif sales >= 20:
            score += 6

        elif sales >= 15:
            score += 5

        elif sales >= 10:
            score += 3

        # -----------------------
        # Profit Growth
        # -----------------------

        profit = stock.get("profit_growth", 0)

        metrics["profit_growth"] = profit

        if profit >= 25:
            score += 7

        elif profit >= 20:
            score += 6

        elif profit >= 15:
            score += 5

        elif profit >= 10:
            score += 3

        # -----------------------
        # EPS Growth
        # -----------------------

        eps = stock.get("eps_growth", 0)

        metrics["eps_growth"] = eps

        if eps >= 25:
            score += 6

        elif eps >= 20:
            score += 5

        elif eps >= 15:
            score += 4

        elif eps >= 10:
            score += 2

        # -----------------------
        # Debt
        # -----------------------

        debt = stock.get("debt_equity", 999)

        metrics["debt_equity"] = debt

        if debt <= 0.25:
            score += 8

        elif debt <= 0.5:
            score += 7

        elif debt <= 1:
            score += 5

        elif debt <= 2:
            score += 2

        else:
            warnings.append("High Debt")

        # -----------------------
        # Promoter Holding
        # -----------------------

        promoter = stock.get("promoter_holding", 0)

        metrics["promoter_holding"] = promoter

        if promoter >= 70:
            score += 6

        elif promoter >= 60:
            score += 5

        elif promoter >= 50:
            score += 4

        else:
            warnings.append("Low Promoter Holding")

        # -----------------------
        # Pledged Shares
        # -----------------------

        pledged = stock.get("pledged", 100)

        metrics["pledged"] = pledged

        if pledged == 0:
            score += 5

        elif pledged <= 5:
            score += 4

        elif pledged <= 10:
            score += 2

        else:
            warnings.append("Promoter Shares Pledged")

        # -----------------------

        passed = score >= self.cfg["minimum_score"]

        confidence = round((score / 53) * 100, 2)

        if confidence >= 90:
            grade = "A+"

        elif confidence >= 80:
            grade = "A"

        elif confidence >= 70:
            grade = "B"

        elif confidence >= 60:
            grade = "C"

        else:
            grade = "D"

        return EngineResult(
            engine="Fundamental",
            passed=passed,
            score=score,
            confidence=confidence,
            grade=grade,
            reasons=reasons,
            warnings=warnings,
            metrics=metrics
        )