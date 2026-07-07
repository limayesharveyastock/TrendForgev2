"""
TrendForge v2
Scoring Engine
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
import json
from pathlib import Path
logger = logging.getLogger(__name__)


# ==========================================================
# SCORE RESULT
# ==========================================================

@dataclass(slots=True)
class ScoreResult:

    total: float = 0.0

    technical: float = 0.0

    fundamental: float = 0.0

    options: float = 0.0

    corporate: float = 0.0

    risk: float = 0.0

    confidence: float = 0.0

    reasons: list = field(default_factory=list)


# ==========================================================
# SCORING ENGINE
# ==========================================================

class ScoringEngine:

    def __init__(self, weights=None):

    self.weights = (

        weights

        if weights

        else self.load_weights()

    )

    # ------------------------------------------------------

    def add(
        self,
        result: ScoreResult,
        key: str,
        condition: bool,
        category: str,
        reason: str,
    ):

        if not condition:
            return

        value = self.weights.get(key, 0)

        result.total += value

        setattr(
            result,
            category,
            getattr(result, category) + value,
        )

        result.reasons.append(reason)

    # ------------------------------------------------------

    def technical_score(
        self,
        latest,
        rules,
        result,
    ):

        self.add(
            result,
            "EMA_ALIGNMENT",
            rules.ema_bullish(latest),
            "technical",
            "EMA Alignment",
        )

        self.add(
            result,
            "RSI",
            rules.rsi_bullish(latest),
            "technical",
            "Healthy RSI",
        )

        self.add(
            result,
            "MACD",
            rules.macd_bullish(latest),
            "technical",
            "MACD Bullish",
        )

        self.add(
            result,
            "ADX",
            rules.adx_strong(latest),
            "technical",
            "Strong ADX",
        )

        self.add(
            result,
            "RVOL",
            rules.high_volume(latest),
            "technical",
            "High Relative Volume",
        )

        self.add(
            result,
            "BREAKOUT",
            rules.breakout(latest),
            "technical",
            "20-Day Breakout",
        )

    # ------------------------------------------------------

    def fundamental_score(
        self,
        fundamentals,
        rules,
        result,
    ):

        if fundamentals is None:
            return

        self.add(
            result,
            "ROE",
            fundamentals.roe > 15,
            "fundamental",
            "ROE > 15%",
        )

        self.add(
            result,
            "ROCE",
            fundamentals.roce > 15,
            "fundamental",
            "ROCE > 15%",
        )

        self.add(
            result,
            "PE",
            0 < fundamentals.pe < 30,
            "fundamental",
            "Healthy PE",
        )

        self.add(
            result,
            "DEBT",
            fundamentals.debt_to_equity < 0.5,
            "fundamental",
            "Low Debt",
        )

        self.add(
            result,
            "SALES_GROWTH",
            fundamentals.sales_growth > 10,
            "fundamental",
            "Sales Growth",
        )

        self.add(
            result,
            "PROFIT_GROWTH",
            fundamentals.profit_growth > 10,
            "fundamental",
            "Profit Growth",
        )

    # ------------------------------------------------------

    def options_score(
        self,
        latest,
        rules,
        result,
    ):

        self.add(
            result,
            "LONG_BUILDUP",
            rules.long_buildup(latest),
            "options",
            "Long Build-up",
        )

        self.add(
            result,
            "SHORT_COVERING",
            rules.short_covering(latest),
            "options",
            "Short Covering",
        )

    # ------------------------------------------------------

    def corporate_score(
        self,
        fundamentals,
        rules,
        result,
    ):

        if fundamentals is None:
            return

        self.add(
            result,
            "EARNINGS",
            rules.earnings_today(fundamentals),
            "corporate",
            "Earnings Event",
        )

        self.add(
            result,
            "BONUS",
            rules.bonus_issue(fundamentals),
            "corporate",
            "Bonus Issue",
        )

        self.add(
            result,
            "DIVIDEND",
            rules.dividend_today(fundamentals),
            "corporate",
            "Dividend",
        )

    # ------------------------------------------------------

    def calculate_confidence(
        self,
        result,
    ):

        result.confidence = min(
            100,
            round(result.total),
        )

    # ------------------------------------------------------

    def score(
        self,
        latest,
        rules,
        fundamentals=None,
    ):

        result = ScoreResult()

        self.technical_score(
            latest,
            rules,
            result,
        )

        self.fundamental_score(
            fundamentals,
            rules,
            result,
        )

        self.options_score(
            latest,
            rules,
            result,
        )

        self.corporate_score(
            fundamentals,
            rules,
            result,
        )

        self.calculate_confidence(
            result,
        )

        return result

    # ------------------------------------------------------

    def update_weight(
    self,
    key,
    value,
):

    self.weights[key] = value

    self.save_weights()

    # ------------------------------------------------------

    def reset_weights(self):

    self.weights = self.load_weights()

    # ------------------------------------------------------

    def health(
        self,
    ):

        return {

            "status": "healthy",

            "weights_loaded": len(self.weights),

            "version": "2.0",

        }
        CONFIG_DIR = Path("config")

        WEIGHTS_FILE = (
        CONFIG_DIR /
        "scoring_weights.json"
        )    
        @staticmethod
def load_weights():

    if not WEIGHTS_FILE.exists():

        raise FileNotFoundError(
            WEIGHTS_FILE
        )

    with open(
        WEIGHTS_FILE,
        "r",
        encoding="utf8",
    ) as f:

        return json.load(f)
        def save_weights(self):

    with open(
        WEIGHTS_FILE,
        "w",
        encoding="utf8",
    ) as f:

        json.dump(
            self.weights,
            f,
            indent=4,
        )