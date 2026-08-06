"""
TrendForge v2
Signal Engine

Converts scoring output into a normalized trading signal.

Flow:

Indicators
    ↓
Rules
    ↓
Scoring Engine
    ↓
Signal Engine
    ↓
BUY / SELL / HOLD
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


@dataclass
class SignalResult:
    """
    Normalized TrendForge signal.
    """

    signal: str = "HOLD"
    confidence: float = 0.0
    score: float = 0.0

    strength: str = "WEAK"

    entry: float | None = None
    stop_loss: float | None = None
    target_1: float | None = None
    target_2: float | None = None

    risk_reward: float | None = None

    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    symbol: str | None = None
    timeframe: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class SignalEngine:
    """
    Final decision layer for TrendForge.

    IMPORTANT:
        This engine does not fetch market data.

    It consumes the output of ScoringEngine and converts
    it into a standardized signal object.
    """

    VERSION = "2.1"

    BUY_THRESHOLD = 70.0
    SELL_THRESHOLD = -30.0

    STRONG_BUY_CONFIDENCE = 80.0
    BUY_CONFIDENCE = 65.0
    STRONG_SELL_CONFIDENCE = 80.0
    SELL_CONFIDENCE = 65.0

    MIN_RISK_REWARD = 1.5

    # =========================================================
    # SAFE HELPERS
    # =========================================================

    @staticmethod
    def _get(
        data: Any,
        key: str,
        default: Any = None,
    ) -> Any:

        if data is None:
            return default

        if isinstance(data, Mapping):
            return data.get(key, default)

        return getattr(
            data,
            key,
            default,
        )

    @staticmethod
    def _number(
        data: Any,
        key: str,
        default: float | None = None,
    ) -> float | None:

        value = SignalEngine._get(
            data,
            key,
            default,
        )

        if value is None:
            return default

        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _list(
        data: Any,
        key: str,
    ) -> list[str]:

        value = SignalEngine._get(
            data,
            key,
            [],
        )

        if value is None:
            return []

        if isinstance(value, str):
            return [value]

        try:
            return list(value)
        except TypeError:
            return []

    # =========================================================
    # SCORE NORMALIZATION
    # =========================================================

    @classmethod
    def normalize_score(
        cls,
        score: float,
        maximum_score: float | None = None,
    ) -> float:

        if maximum_score is not None and maximum_score > 0:

            normalized = (
                score
                / maximum_score
                * 100.0
            )

            return max(
                -100.0,
                min(
                    100.0,
                    normalized,
                ),
            )

        return max(
            -100.0,
            min(
                100.0,
                score,
            ),
        )

    # =========================================================
    # SIGNAL FROM SCORE
    # =========================================================

    @classmethod
    def signal_from_score(
        cls,
        score: float,
        confidence: float = 0.0,
    ) -> str:

        if (
            score >= cls.BUY_THRESHOLD
            and confidence >= cls.BUY_CONFIDENCE
        ):
            return "BUY"

        if (
            score <= cls.SELL_THRESHOLD
            and confidence >= cls.SELL_CONFIDENCE
        ):
            return "SELL"

        return "HOLD"

    # =========================================================
    # STRENGTH
    # =========================================================

    @classmethod
    def calculate_strength(
        cls,
        signal: str,
        confidence: float,
    ) -> str:

        if signal == "BUY":

            if confidence >= cls.STRONG_BUY_CONFIDENCE:
                return "STRONG"

            if confidence >= cls.BUY_CONFIDENCE:
                return "MODERATE"

            return "WEAK"

        if signal == "SELL":

            if confidence >= cls.STRONG_SELL_CONFIDENCE:
                return "STRONG"

            if confidence >= cls.SELL_CONFIDENCE:
                return "MODERATE"

            return "WEAK"

        return "NEUTRAL"

    # =========================================================
    # RISK / REWARD
    # =========================================================

    @staticmethod
    def calculate_risk_reward(
        entry: float | None,
        stop_loss: float | None,
        target: float | None,
        signal: str,
    ) -> float | None:

        if (
            entry is None
            or stop_loss is None
            or target is None
        ):
            return None

        risk = abs(
            entry - stop_loss
        )

        if risk <= 0:
            return None

        if signal == "SELL":

            reward = abs(
                entry - target
            )

        else:

            reward = abs(
                target - entry
            )

        return reward / risk

    # =========================================================
    # PRICE LEVELS
    # =========================================================

    @staticmethod
    def extract_price_levels(
        market_data: Any,
        signal: str,
    ) -> tuple[
        float | None,
        float | None,
        float | None,
        float | None,
    ]:

        entry = SignalEngine._number(
            market_data,
            "entry",
        )

        if entry is None:

            entry = SignalEngine._number(
                market_data,
                "close",
            )

        stop_loss = SignalEngine._number(
            market_data,
            "stop_loss",
        )

        target_1 = SignalEngine._number(
            market_data,
            "target_1",
        )

        target_2 = SignalEngine._number(
            market_data,
            "target_2",
        )

        return (
            entry,
            stop_loss,
            target_1,
            target_2,
        )

    # =========================================================
    # VALIDATE RISK
    # =========================================================

    @classmethod
    def validate_risk_reward(
        cls,
        result: SignalResult,
    ) -> None:

        if result.signal == "HOLD":
            return

        if result.risk_reward is None:

            result.warnings.append(
                "Risk/reward could not be calculated"
            )

            return

        if result.risk_reward < cls.MIN_RISK_REWARD:

            result.warnings.append(
                f"Risk/reward below "
                f"{cls.MIN_RISK_REWARD:.1f}:1"
            )

    # =========================================================
    # CONFIDENCE
    # =========================================================

    @staticmethod
    def calculate_confidence(
        scoring_result: Any,
    ) -> float:

        confidence = SignalEngine._number(
            scoring_result,
            "confidence",
            0.0,
        )

        if confidence is None:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        )

    # =========================================================
    # MASTER BUILD
    # =========================================================

    def generate(
        self,
        scoring_result: Any,
        market_data: Any = None,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> SignalResult:

        raw_score = self._number(
            scoring_result,
            "total",
            None,
        )

        if raw_score is None:

            raw_score = self._number(
                scoring_result,
                "score",
                0.0,
            )

        confidence = self.calculate_confidence(
            scoring_result
        )

        supplied_signal = self._get(
            scoring_result,
            "signal",
            None,
        )

        score = float(
            raw_score or 0.0
        )

        signal = self.signal_from_score(
            score,
            confidence,
        )

        # If ScoringEngine already supplied a valid
        # signal, use it only when confidence supports it.
        if supplied_signal in {
            "BUY",
            "SELL",
        }:

            calculated_signal = signal

            if calculated_signal == supplied_signal:
                signal = supplied_signal

        reasons = self._list(
            scoring_result,
            "reasons",
        )

        warnings = self._list(
            scoring_result,
            "warnings",
        )

        (
            entry,
            stop_loss,
            target_1,
            target_2,
        ) = self.extract_price_levels(
            market_data,
            signal,
        )

        risk_reward = self.calculate_risk_reward(
            entry,
            stop_loss,
            target_1,
            signal,
        )

        result = SignalResult(
            signal=signal,
            confidence=round(
                confidence,
                2,
            ),
            score=round(
                score,
                2,
            ),
            strength=self.calculate_strength(
                signal,
                confidence,
            ),
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            risk_reward=(
                round(
                    risk_reward,
                    2,
                )
                if risk_reward is not None
                else None
            ),
            reasons=reasons,
            warnings=warnings,
            symbol=symbol,
            timeframe=timeframe,
        )

        self.validate_risk_reward(
            result
        )

        return result

    # =========================================================
    # DICT API
    # =========================================================

    def generate_dict(
        self,
        scoring_result: Any,
        market_data: Any = None,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> dict[str, Any]:

        return self.generate(
            scoring_result=scoring_result,
            market_data=market_data,
            symbol=symbol,
            timeframe=timeframe,
        ).as_dict()

    # =========================================================
    # CONVENIENCE METHODS
    # =========================================================

    def is_buy(
        self,
        scoring_result: Any,
    ) -> bool:

        return (
            self.generate(
                scoring_result
            ).signal
            == "BUY"
        )

    def is_sell(
        self,
        scoring_result: Any,
    ) -> bool:

        return (
            self.generate(
                scoring_result
            ).signal
            == "SELL"
        )

    def is_hold(
        self,
        scoring_result: Any,
    ) -> bool:

        return (
            self.generate(
                scoring_result
            ).signal
            == "HOLD"
        )

    # =========================================================
    # HEALTH
    # =========================================================

    def health(self) -> dict[str, Any]:

        return {
            "status": "healthy",
            "version": self.VERSION,
            "buy_threshold": self.BUY_THRESHOLD,
            "sell_threshold": self.SELL_THRESHOLD,
            "buy_confidence": self.BUY_CONFIDENCE,
            "sell_confidence": self.SELL_CONFIDENCE,
            "minimum_risk_reward": self.MIN_RISK_REWARD,
        }


# =============================================================
# MODULE-LEVEL CONVENIENCE
# =============================================================

_default_engine = SignalEngine()


def generate_signal(
    scoring_result: Any,
    market_data: Any = None,
    symbol: str | None = None,
    timeframe: str | None = None,
) -> dict[str, Any]:

    """
    Simple public API for other TrendForge modules.
    """

    return _default_engine.generate_dict(
        scoring_result=scoring_result,
        market_data=market_data,
        symbol=symbol,
        timeframe=timeframe,
    )