"""
TrendForge v2 - Scoring Engine

Central deterministic scoring layer.

Flow:
Indicators -> Rules -> Scoring -> Signal

Produces:
- component scores
- total score
- confidence
- BUY / HOLD / SELL
- reasons
- warnings
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

logger = logging.getLogger(__name__)


# ============================================================
# SCORE RESULT
# ============================================================

@dataclass
class ScoreResult:
    total: float = 0.0

    technical: float = 0.0
    fundamental: float = 0.0
    options: float = 0.0
    corporate: float = 0.0
    risk: float = 0.0

    confidence: float = 0.0
    signal: str = "HOLD"

    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "total": round(self.total, 2),
            "technical": round(self.technical, 2),
            "fundamental": round(self.fundamental, 2),
            "options": round(self.options, 2),
            "corporate": round(self.corporate, 2),
            "risk": round(self.risk, 2),
            "confidence": round(self.confidence, 2),
            "signal": self.signal,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
        }


# ============================================================
# SCORING ENGINE
# ============================================================

class ScoringEngine:
    """
    Master TrendForge scoring engine.

    Positive conditions increase the score.
    Negative conditions reduce the score.

    The engine itself does not fetch market data.
    """

    CONFIG_DIR = Path("config")
    WEIGHTS_FILE = CONFIG_DIR / "scoring_weights.json"

    BUY_THRESHOLD = 70.0
    SELL_THRESHOLD = -30.0

    VERSION = "2.1"

    def __init__(
        self,
        weights: Mapping[str, float] | None = None,
    ) -> None:

        if weights is not None:
            self.weights = {
                str(key): float(value)
                for key, value in weights.items()
            }
        else:
            self.weights = self.load_weights()

    # ========================================================
    # CONFIGURATION
    # ========================================================

    @classmethod
    def load_weights(cls) -> dict[str, float]:
        """Load scoring weights from JSON configuration."""

        if not cls.WEIGHTS_FILE.exists():
            logger.warning(
                "Scoring weights file not found: %s",
                cls.WEIGHTS_FILE,
            )
            return {}

        try:
            with cls.WEIGHTS_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError) as exc:
            logger.error(
                "Unable to load scoring weights: %s",
                exc,
            )
            return {}

        if not isinstance(data, dict):
            raise ValueError(
                "scoring_weights.json must contain a JSON object"
            )

        return {
            str(key): float(value)
            for key, value in data.items()
        }

    def save_weights(self) -> None:
        """Persist current weights."""

        self.CONFIG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.WEIGHTS_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.weights,
                file,
                indent=4,
            )

    def update_weight(
        self,
        key: str,
        value: float,
    ) -> None:
        self.weights[str(key)] = float(value)
        self.save_weights()

    def reset_weights(self) -> None:
        self.weights = self.load_weights()

    # ========================================================
    # SAFE DATA ACCESS
    # ========================================================

    @staticmethod
    def _get(
        source: Any,
        key: str,
        default: Any = None,
    ) -> Any:
        """Read from dict-like objects or normal objects."""

        if source is None:
            return default

        if isinstance(source, Mapping):
            return source.get(key, default)

        try:
            return getattr(
                source,
                key,
                default,
            )
        except Exception:
            return default

    @staticmethod
    def _number(
        source: Any,
        key: str,
        default: float = 0.0,
    ) -> float:
        """Safely convert a value to float."""

        value = ScoringEngine._get(
            source,
            key,
            default,
        )

        try:
            if value is None:
                return default

            return float(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _rule(
        rules: Any,
        name: str,
        value: Any,
    ) -> bool:
        """Safely execute a rule function."""

        function = getattr(
            rules,
            name,
            None,
        )

        if not callable(function):
            return False

        try:
            return bool(
                function(value)
            )

        except (
            KeyError,
            TypeError,
            ValueError,
            AttributeError,
            IndexError,
        ):
            return False

    def _weight(
        self,
        key: str,
    ) -> float:
        return float(
            self.weights.get(
                key,
                0.0,
            )
        )

    # ========================================================
    # SCORE ADDITION
    # ========================================================

    def _add(
        self,
        result: ScoreResult,
        key: str,
        condition: bool,
        category: str,
        reason: str,
        multiplier: float = 1.0,
    ) -> None:
        """
        Add weighted score when condition is true.

        multiplier=-1 means the condition is bearish.
        """

        if not condition:
            return

        value = (
            self._weight(key)
            * multiplier
        )

        if value == 0:
            return

        result.total += value

        current = getattr(
            result,
            category,
        )

        setattr(
            result,
            category,
            current + value,
        )

        if value > 0:
            result.reasons.append(reason)
        else:
            result.warnings.append(reason)

    # ========================================================
    # TECHNICAL
    # ========================================================

    def technical_score(
        self,
        latest: Any,
        rules: Any,
        result: ScoreResult,
    ) -> None:

        self._add(
            result,
            "EMA_ALIGNMENT",
            self._rule(
                rules,
                "ema_bullish",
                latest,
            ),
            "technical",
            "EMA alignment bullish",
        )

        self._add(
            result,
            "EMA_GOLDEN_CROSS",
            self._rule(
                rules,
                "golden_cross",
                latest,
            ),
            "technical",
            "Golden cross confirmed",
        )

        self._add(
            result,
            "EMA_GOLDEN_CROSS",
            self._rule(
                rules,
                "death_cross",
                latest,
            ),
            "technical",
            "Death cross detected",
            -1.0,
        )

        self._add(
            result,
            "RSI",
            self._rule(
                rules,
                "rsi_bullish",
                latest,
            ),
            "technical",
            "RSI bullish",
        )

        self._add(
            result,
            "MACD",
            self._rule(
                rules,
                "macd_bullish",
                latest,
            ),
            "technical",
            "MACD bullish",
        )

        self._add(
            result,
            "ADX",
            self._rule(
                rules,
                "adx_strong",
                latest,
            ),
            "technical",
            "ADX confirms trend strength",
        )

        self._add(
            result,
            "RVOL",
            self._rule(
                rules,
                "high_volume",
                latest,
            ),
            "technical",
            "High relative volume",
        )

        self._add(
            result,
            "VWAP",
            self._rule(
                rules,
                "above_vwap",
                latest,
            ),
            "technical",
            "Price above VWAP",
        )

        self._add(
            result,
            "CMF",
            self._rule(
                rules,
                "positive_money_flow",
                latest,
            ),
            "technical",
            "Positive money flow",
        )

        self._add(
            result,
            "BREAKOUT",
            self._rule(
                rules,
                "breakout",
                latest,
            ),
            "technical",
            "Breakout confirmed",
        )

        self._add(
            result,
            "BREAKOUT",
            self._rule(
                rules,
                "breakdown",
                latest,
            ),
            "technical",
            "Breakdown detected",
            -1.0,
        )

        self._add(
            result,
            "ATR_EXPANSION",
            self._rule(
                rules,
                "atr_expansion",
                latest,
            ),
            "technical",
            "ATR expansion",
        )

        self._add(
            result,
            "BB_SQUEEZE",
            self._rule(
                rules,
                "bb_squeeze",
                latest,
            ),
            "technical",
            "Bollinger squeeze",
        )

        self._add(
            result,
            "ENGULFING",
            self._rule(
                rules,
                "bullish_engulfing",
                latest,
            ),
            "technical",
            "Bullish engulfing",
        )

        self._add(
            result,
            "ENGULFING",
            self._rule(
                rules,
                "bearish_engulfing",
                latest,
            ),
            "technical",
            "Bearish engulfing",
            -1.0,
        )

        self._add(
            result,
            "HAMMER",
            self._rule(
                rules,
                "hammer",
                latest,
            ),
            "technical",
            "Hammer pattern",
        )

    # ========================================================
    # FUNDAMENTAL
    # ========================================================

    def fundamental_score(
        self,
        fundamentals: Any,
        rules: Any,
        result: ScoreResult,
    ) -> None:

        if fundamentals is None:
            return

        self._add(
            result,
            "ROE",
            self._number(
                fundamentals,
                "roe",
            ) >= 15,
            "fundamental",
            "ROE >= 15%",
        )

        self._add(
            result,
            "ROCE",
            self._number(
                fundamentals,
                "roce",
            ) >= 15,
            "fundamental",
            "ROCE >= 15%",
        )

        pe = self._number(
            fundamentals,
            "pe",
        )

        self._add(
            result,
            "PE",
            0 < pe < 30,
            "fundamental",
            "Healthy PE",
        )

        debt = self._number(
            fundamentals,
            "debt_to_equity",
            999,
        )

        self._add(
            result,
            "DEBT",
            debt < 0.5,
            "fundamental",
            "Low debt",
        )

        self._add(
            result,
            "SALES_GROWTH",
            self._number(
                fundamentals,
                "sales_growth",
            ) > 10,
            "fundamental",
            "Sales growth > 10%",
        )

        self._add(
            result,
            "PROFIT_GROWTH",
            self._number(
                fundamentals,
                "profit_growth",
            ) > 10,
            "fundamental",
            "Profit growth > 10%",
        )

        self._add(
            result,
            "PROMOTER",
            self._number(
                fundamentals,
                "promoter_holding",
            ) >= 50,
            "fundamental",
            "Promoter holding >= 50%",
        )

    # ========================================================
    # OPTIONS
    # ========================================================

    def options_score(
        self,
        latest: Any,
        rules: Any,
        result: ScoreResult,
    ) -> None:

        self._add(
            result,
            "LONG_BUILDUP",
            self._rule(
                rules,
                "long_buildup",
                latest,
            ),
            "options",
            "Long build-up",
        )

        self._add(
            result,
            "SHORT_COVERING",
            self._rule(
                rules,
                "short_covering",
                latest,
            ),
            "options",
            "Short covering",
        )

        self._add(
            result,
            "LONG_BUILDUP",
            self._rule(
                rules,
                "short_buildup",
                latest,
            ),
            "options",
            "Short build-up",
            -1.0,
        )

        self._add(
            result,
            "LONG_BUILDUP",
            self._rule(
                rules,
                "long_unwinding",
                latest,
            ),
            "options",
            "Long unwinding",
            -1.0,
        )

    # ========================================================
    # CORPORATE
    # ========================================================

    def corporate_score(
        self,
        data: Any,
        rules: Any,
        result: ScoreResult,
    ) -> None:

        if data is None:
            return

        self._add(
            result,
            "EARNINGS",
            self._rule(
                rules,
                "earnings_today",
                data,
            ),
            "corporate",
            "Earnings event",
        )

        self._add(
            result,
            "BONUS",
            self._rule(
                rules,
                "bonus_issue",
                data,
            ),
            "corporate",
            "Bonus issue",
        )

        self._add(
            result,
            "DIVIDEND",
            self._rule(
                rules,
                "dividend_today",
                data,
            ),
            "corporate",
            "Dividend event",
        )

    # ========================================================
    # RISK
    # ========================================================

    def risk_score(
        self,
        latest: Any,
        result: ScoreResult,
    ) -> None:

        high_beta = bool(
            self._get(
                latest,
                "HIGH_BETA",
                False,
            )
        )

        low_liquidity = bool(
            self._get(
                latest,
                "LOW_LIQUIDITY",
                False,
            )
        )

        if high_beta:

            value = self._weight(
                "HIGH_BETA"
            )

            result.total += value
            result.risk += value

            result.warnings.append(
                "High beta risk"
            )

        if low_liquidity:

            value = self._weight(
                "LOW_LIQUIDITY"
            )

            result.total += value
            result.risk += value

            result.warnings.append(
                "Low liquidity risk"
            )

    # ========================================================
    # MAXIMUM SCORE
    # ========================================================

    def maximum_score(self) -> float:

        return sum(
            max(
                value,
                0.0,
            )
            for value in self.weights.values()
        )

    # ========================================================
    # CONFIDENCE
    # ========================================================

    def calculate_confidence(
        self,
        result: ScoreResult,
    ) -> None:

        maximum = self.maximum_score()

        if maximum <= 0:
            result.confidence = 0.0
            return

        result.confidence = max(
            0.0,
            min(
                100.0,
                abs(
                    result.total
                    / maximum
                    * 100.0
                ),
            ),
        )

    # ========================================================
    # SIGNAL
    # ========================================================

    @classmethod
    def signal_from_score(
        cls,
        score: float,
        maximum: float,
    ) -> str:

        if maximum <= 0:
            return "HOLD"

        normalized = (
            score
            / maximum
            * 100.0
        )

        if normalized >= cls.BUY_THRESHOLD:
            return "BUY"

        if normalized <= cls.SELL_THRESHOLD:
            return "SELL"

        return "HOLD"

    # ========================================================
    # MASTER SCORE
    # ========================================================

    def score(
        self,
        latest: Any,
        rules: Any,
        fundamentals: Any = None,
    ) -> ScoreResult:

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

        self.risk_score(
            latest,
            result,
        )

        self.calculate_confidence(
            result,
        )

        result.signal = self.signal_from_score(
            result.total,
            self.maximum_score(),
        )

        return result

    # ========================================================
    # DICT API
    # ========================================================

    def score_dict(
        self,
        latest: Any,
        rules: Any,
        fundamentals: Any = None,
    ) -> dict[str, Any]:

        return self.score(
            latest,
            rules,
            fundamentals,
        ).as_dict()

    # ========================================================
    # HEALTH
    # ========================================================

    def health(self) -> dict[str, Any]:

        return {
            "status": "healthy",
            "version": self.VERSION,
            "weights_loaded": len(
                self.weights
            ),
            "maximum_score": round(
                self.maximum_score(),
                2,
            ),
            "buy_threshold": self.BUY_THRESHOLD,
            "sell_threshold": self.SELL_THRESHOLD,
        }