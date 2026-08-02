from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

from engines.base_engine import BaseEngine, EngineResult


class BreakoutEngine(BaseEngine):

    NAME = "Breakout Engine"
    priority = 8
    mandatory = False

    def __init__(self, provider=None):
        self.provider = provider

    def evaluate(self, stock: Dict[str, Any]) -> EngineResult:
        data = self._data(stock)
        symbol = str(
            data.get("symbol")
            or data.get("ticker")
            or data.get("tradingsymbol")
            or ""
        ).upper()

        price = self._number(
            data.get("close")
            or data.get("ltp")
            or data.get("price")
        )

        high = self._number(
            data.get("high")
        )

        low = self._number(
            data.get("low")
        )

        resistance = self._number(
            data.get("resistance")
            or data.get("resistance_level")
            or data.get("nearest_resistance")
        )

        support = self._number(
            data.get("support")
            or data.get("support_level")
            or data.get("nearest_support")
        )

        previous_high = self._number(
            data.get("previous_high")
            or data.get("prior_high")
            or data.get("swing_high")
            or data.get("recent_high")
        )

        previous_low = self._number(
            data.get("previous_low")
            or data.get("prior_low")
            or data.get("swing_low")
            or data.get("recent_low")
        )

        volume_ratio = self._number(
            data.get("volume_ratio")
            or data.get("rvol")
            or data.get("relative_volume")
        )

        volume_ma = self._number(
            data.get("volume_ma")
            or data.get("volume_average")
        )

        volume = self._number(
            data.get("volume")
        )

        breakout_flag = self._boolean(
            data.get("breakout")
            or data.get("is_breakout")
        )

        breakdown_flag = self._boolean(
            data.get("breakdown")
            or data.get("is_breakdown")
        )

        breakout = False
        breakdown = False
        reasons: List[str] = []
        warnings: List[str] = []

        if price is not None:
            if resistance is not None:
                breakout = price > resistance

            if previous_high is not None:
                breakout = breakout or price > previous_high

            if support is not None:
                breakdown = price < support

            if previous_low is not None:
                breakdown = breakdown or price < previous_low

        if breakout_flag is True:
            breakout = True

        if breakdown_flag is True:
            breakdown = True

        if breakout and breakdown:
            direction = "CONFLICT"
            score = 50.0
            warnings.append(
                "Breakout and breakdown conditions conflict."
            )
        elif breakout:
            direction = "BREAKOUT"
            score = 68.0
            reasons.append(
                "Price is breaking above a key reference level."
            )
        elif breakdown:
            direction = "BREAKDOWN"
            score = 32.0
            reasons.append(
                "Price is breaking below a key reference level."
            )
        else:
            direction = "RANGE"
            score = 50.0

        volume_confirmation = self._volume_confirmation(
            volume_ratio,
            volume,
            volume_ma,
        )

        if direction == "BREAKOUT":
            score += volume_confirmation
        elif direction == "BREAKDOWN":
            score -= volume_confirmation

        if direction == "BREAKOUT":
            if volume_confirmation >= 10:
                reasons.append(
                    "Breakout has strong volume confirmation."
                )
            elif volume_confirmation <= 3:
                warnings.append(
                    "Breakout lacks strong volume confirmation."
                )

        elif direction == "BREAKDOWN":
            if volume_confirmation >= 10:
                reasons.append(
                    "Breakdown has strong volume confirmation."
                )
            elif volume_confirmation <= 3:
                warnings.append(
                    "Breakdown lacks strong volume confirmation."
                )

        distance = self._break_distance(
            price,
            resistance if direction == "BREAKOUT" else support,
        )

        if distance is not None:
            if direction == "BREAKOUT" and distance >= 2:
                reasons.append(
                    "Price has moved decisively beyond resistance."
                )
            elif direction == "BREAKDOWN" and distance >= 2:
                reasons.append(
                    "Price has moved decisively below support."
                )

        score = self._clamp(
            score,
            0,
            100,
        )

        quality = self._quality(
            price,
            resistance,
            support,
            previous_high,
            previous_low,
            volume_ratio,
            volume,
            volume_ma,
        )

        confidence = self._confidence(
            quality,
            direction,
            volume_confirmation,
        )

        passed = (
            direction == "BREAKOUT"
            and score >= 65
        )

        if direction == "RANGE":
            passed = False

        return EngineResult(
            engine=self.NAME,
            passed=passed,
            score=round(score, 2),
            confidence=round(confidence, 2),
            grade=self._grade(score),
            reasons=self._dedupe(reasons),
            warnings=self._dedupe(warnings),
            metrics={
                "symbol": symbol,
                "direction": direction,
                "breakout": breakout,
                "breakdown": breakdown,
                "price": price,
                "resistance": resistance,
                "support": support,
                "previous_high": previous_high,
                "previous_low": previous_low,
                "volume_ratio": volume_ratio,
                "volume": volume,
                "volume_ma": volume_ma,
                "volume_confirmation": round(
                    volume_confirmation,
                    2,
                ),
                "distance_from_level_pct": (
                    round(distance, 3)
                    if distance is not None
                    else None
                ),
                "data_quality": quality,
            },
        )

    def scan(
        self,
        stocks: Iterable[Mapping[str, Any]],
    ) -> List[EngineResult]:
        results = []

        for stock in stocks:
            try:
                results.append(
                    self.evaluate(
                        dict(stock)
                    )
                )
            except Exception:
                continue

        return results

    @staticmethod
    def _data(
        stock: Any,
    ) -> Dict[str, Any]:
        if isinstance(stock, Mapping):
            return dict(stock)

        if hasattr(stock, "__dict__"):
            try:
                return dict(vars(stock))
            except Exception:
                return {}

        return {}

    def _volume_confirmation(
        self,
        volume_ratio: Optional[float],
        volume: Optional[float],
        volume_ma: Optional[float],
    ) -> float:

        ratio = volume_ratio

        if (
            ratio is None
            and volume is not None
            and volume_ma is not None
            and volume_ma > 0
        ):
            ratio = volume / volume_ma

        if ratio is None:
            return 0.0

        if ratio >= 2.0:
            return 18.0

        if ratio >= 1.5:
            return 15.0

        if ratio >= 1.25:
            return 11.0

        if ratio >= 1.10:
            return 7.0

        if ratio >= 1.0:
            return 4.0

        return 0.0

    @staticmethod
    def _break_distance(
        price: Optional[float],
        level: Optional[float],
    ) -> Optional[float]:

        if (
            price is None
            or level is None
            or level == 0
        ):
            return None

        return abs(
            price - level
        ) / abs(level) * 100

    @staticmethod
    def _quality(
        price: Optional[float],
        resistance: Optional[float],
        support: Optional[float],
        previous_high: Optional[float],
        previous_low: Optional[float],
        volume_ratio: Optional[float],
        volume: Optional[float],
        volume_ma: Optional[float],
    ) -> str:

        fields = (
            price,
            resistance,
            support,
            previous_high,
            previous_low,
            volume_ratio,
            volume,
            volume_ma,
        )

        count = sum(
            value is not None
            for value in fields
        )

        if count >= 6:
            return "HIGH"

        if count >= 4:
            return "MEDIUM"

        if count >= 2:
            return "LOW"

        return "NONE"

    @staticmethod
    def _confidence(
        quality: str,
        direction: str,
        volume_confirmation: float,
    ) -> float:

        base = {
            "HIGH": 78.0,
            "MEDIUM": 62.0,
            "LOW": 42.0,
            "NONE": 15.0,
        }.get(
            quality,
            15.0,
        )

        if direction in (
            "BREAKOUT",
            "BREAKDOWN",
        ):
            base += min(
                volume_confirmation,
                12,
            )

        return max(
            0.0,
            min(
                100.0,
                base,
            ),
        )

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:

        if value is None or value == "":
            return None

        try:
            if isinstance(value, str):
                value = (
                    value.replace(",", "")
                    .replace("%", "")
                    .replace("₹", "")
                    .strip()
                )

            result = float(value)

            if math.isfinite(result):
                return result

        except (
            TypeError,
            ValueError,
        ):
            return None

        return None

    @staticmethod
    def _boolean(
        value: Any,
    ) -> Optional[bool]:

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            text = value.strip().lower()

            if text in (
                "true",
                "yes",
                "1",
                "breakout",
            ):
                return True

            if text in (
                "false",
                "no",
                "0",
                "none",
            ):
                return False

        if isinstance(value, (int, float)):
            return bool(value)

        return None

    @staticmethod
    def _clamp(
        value: float,
        low: float,
        high: float,
    ) -> float:

        return max(
            low,
            min(
                high,
                float(value),
            ),
        )

    @staticmethod
    def _grade(
        score: float,
    ) -> str:

        if score >= 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        if score >= 45:
            return "D"
        return "F"

    @staticmethod
    def _dedupe(
        values: Iterable[str],
    ) -> List[str]:

        result = []
        seen = set()

        for value in values:
            text = str(value).strip()

            if text and text not in seen:
                seen.add(text)
                result.append(text)

        return result

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "engine": self.NAME,
            "priority": self.priority,
            "mandatory": self.mandatory,
            "coverage": [
                "breakout detection",
                "breakdown detection",
                "resistance break",
                "support break",
                "volume confirmation",
                "relative volume",
            ],
        }


def get_breakout_engine(
    provider=None,
) -> BreakoutEngine:
    return BreakoutEngine(
        provider=provider
    )


__all__ = [
    "BreakoutEngine",
    "get_breakout_engine",
]