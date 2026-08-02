from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

from engines.base_engine import BaseEngine, EngineResult


class SupportResistanceEngine(BaseEngine):

    NAME = "Support Resistance Engine"
    priority = 12
    mandatory = False

    def __init__(self, provider=None):
        self.provider = provider

    def evaluate(self, stock: Mapping[str, Any]) -> EngineResult:
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

        supports = self._levels(
            data.get("supports")
            or data.get("support_levels")
        )

        resistances = self._levels(
            data.get("resistances")
            or data.get("resistance_levels")
        )

        support = self._number(
            data.get("support")
            or data.get("nearest_support")
            or data.get("support_level")
        )

        resistance = self._number(
            data.get("resistance")
            or data.get("nearest_resistance")
            or data.get("resistance_level")
        )

        if support is not None:
            supports.append(support)

        if resistance is not None:
            resistances.append(resistance)

        supports = self._unique_levels(supports)
        resistances = self._unique_levels(resistances)

        nearest_support = self._nearest_below(
            price,
            supports,
        )

        nearest_resistance = self._nearest_above(
            price,
            resistances,
        )

        support_distance = self._distance(
            price,
            nearest_support,
        )

        resistance_distance = self._distance(
            price,
            nearest_resistance,
        )

        direction = self._direction(
            price,
            nearest_support,
            nearest_resistance,
        )

        score = self._score(
            price,
            nearest_support,
            nearest_resistance,
            support_distance,
            resistance_distance,
        )

        reasons = self._reasons(
            direction,
            support_distance,
            resistance_distance,
            nearest_support,
            nearest_resistance,
        )

        warnings = self._warnings(
            price,
            nearest_support,
            nearest_resistance,
        )

        quality = self._quality(
            price,
            supports,
            resistances,
        )

        confidence = {
            "HIGH": 84.0,
            "MEDIUM": 68.0,
            "LOW": 45.0,
            "NONE": 15.0,
        }.get(
            quality,
            15.0,
        )

        return EngineResult(
            engine=self.NAME,
            passed=direction in (
                "SUPPORT_HOLD",
                "BULLISH_SPACE",
                "RESISTANCE_BREAK",
            ),
            score=round(score, 2),
            confidence=round(confidence, 2),
            grade=self._grade(score),
            reasons=self._dedupe(reasons),
            warnings=self._dedupe(warnings),
            metrics={
                "symbol": symbol,
                "direction": direction,
                "price": price,
                "nearest_support": nearest_support,
                "nearest_resistance": nearest_resistance,
                "support_distance_pct": (
                    round(support_distance, 3)
                    if support_distance is not None
                    else None
                ),
                "resistance_distance_pct": (
                    round(resistance_distance, 3)
                    if resistance_distance is not None
                    else None
                ),
                "support_count": len(supports),
                "resistance_count": len(resistances),
                "supports": supports[:10],
                "resistances": resistances[:10],
                "data_quality": quality,
            },
        )

    def _direction(
        self,
        price: Optional[float],
        support: Optional[float],
        resistance: Optional[float],
    ) -> str:

        if price is None:
            return "UNKNOWN"

        if (
            resistance is not None
            and price > resistance
        ):
            return "RESISTANCE_BREAK"

        if (
            support is not None
            and price < support
        ):
            return "SUPPORT_BREAK"

        if (
            support is not None
            and self._distance(
                price,
                support,
            ) is not None
            and self._distance(
                price,
                support,
            ) <= 1.0
        ):
            return "SUPPORT_HOLD"

        if (
            resistance is not None
            and self._distance(
                price,
                resistance,
            ) is not None
            and self._distance(
                price,
                resistance,
            ) <= 1.0
        ):
            return "RESISTANCE_TEST"

        if (
            support is not None
            and resistance is not None
        ):
            return "BULLISH_SPACE"

        if support is not None:
            return "ABOVE_SUPPORT"

        if resistance is not None:
            return "BELOW_RESISTANCE"

        return "UNKNOWN"

    def _score(
        self,
        price: Optional[float],
        support: Optional[float],
        resistance: Optional[float],
        support_distance: Optional[float],
        resistance_distance: Optional[float],
    ) -> float:

        if price is None:
            return 50.0

        if (
            resistance is not None
            and price > resistance
        ):
            return 88.0

        if (
            support is not None
            and price < support
        ):
            return 18.0

        score = 50.0

        if (
            support_distance is not None
            and support_distance <= 1.0
        ):
            score += 15.0

        elif (
            support_distance is not None
            and support_distance <= 2.5
        ):
            score += 8.0

        if (
            resistance_distance is not None
            and resistance_distance <= 1.0
        ):
            score -= 8.0

        elif (
            resistance_distance is not None
            and resistance_distance <= 2.5
        ):
            score -= 3.0

        if (
            support is not None
            and resistance is not None
            and resistance > support
        ):
            room = (
                price - support
            ) / (
                resistance - support
            )

            if room < 0.35:
                score += 8.0

            elif room > 0.8:
                score -= 8.0

        return self._clamp(
            score,
            0,
            100,
        )

    def _reasons(
        self,
        direction: str,
        support_distance: Optional[float],
        resistance_distance: Optional[float],
        support: Optional[float],
        resistance: Optional[float],
    ) -> List[str]:

        reasons = []

        if direction == "SUPPORT_HOLD":
            reasons.append(
                "Price is close to support."
            )

        elif direction == "RESISTANCE_TEST":
            reasons.append(
                "Price is testing nearby resistance."
            )

        elif direction == "RESISTANCE_BREAK":
            reasons.append(
                "Price is above the nearest resistance level."
            )

        elif direction == "SUPPORT_BREAK":
            reasons.append(
                "Price is below the nearest support level."
            )

        elif direction == "BULLISH_SPACE":
            reasons.append(
                "Price has identifiable support and resistance with room toward resistance."
            )

        if (
            support_distance is not None
            and support_distance <= 1.0
        ):
            reasons.append(
                "Downside is close to a defined support zone."
            )

        if (
            resistance_distance is not None
            and resistance_distance <= 1.0
        ):
            reasons.append(
                "Upside is close to a defined resistance zone."
            )

        return self._dedupe(reasons)

    def _warnings(
        self,
        price: Optional[float],
        support: Optional[float],
        resistance: Optional[float],
    ) -> List[str]:

        warnings = []

        if price is None:
            warnings.append(
                "Current price unavailable."
            )

        if support is None:
            warnings.append(
                "Support level unavailable."
            )

        if resistance is None:
            warnings.append(
                "Resistance level unavailable."
            )

        return warnings

    @staticmethod
    def _quality(
        price: Optional[float],
        supports: List[float],
        resistances: List[float],
    ) -> str:

        count = (
            int(price is not None)
            + min(len(supports), 2)
            + min(len(resistances), 2)
        )

        if count >= 5:
            return "HIGH"

        if count >= 3:
            return "MEDIUM"

        if count >= 1:
            return "LOW"

        return "NONE"

    @staticmethod
    def _nearest_below(
        price: Optional[float],
        levels: List[float],
    ) -> Optional[float]:

        if price is None:
            return None

        candidates = [
            level
            for level in levels
            if level < price
        ]

        return max(
            candidates,
            default=None,
        )

    @staticmethod
    def _nearest_above(
        price: Optional[float],
        levels: List[float],
    ) -> Optional[float]:

        if price is None:
            return None

        candidates = [
            level
            for level in levels
            if level > price
        ]

        return min(
            candidates,
            default=None,
        )

    @staticmethod
    def _distance(
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
        ) / abs(level) * 100.0

    @staticmethod
    def _levels(
        value: Any,
    ) -> List[float]:

        if value is None:
            return []

        if isinstance(
            value,
            (int, float),
        ):
            return [
                float(value)
            ]

        if isinstance(value, str):
            values = value.split(",")

            result = []

            for item in values:
                number = SupportResistanceEngine._number(
                    item
                )

                if number is not None:
                    result.append(number)

            return result

        if isinstance(
            value,
            (list, tuple, set),
        ):
            result = []

            for item in value:
                number = SupportResistanceEngine._number(
                    item
                )

                if number is not None:
                    result.append(number)

            return result

        return []

    @staticmethod
    def _unique_levels(
        levels: List[float],
    ) -> List[float]:

        result = []

        for level in sorted(levels):
            if not result:
                result.append(level)
                continue

            if abs(
                level - result[-1]
            ) / max(
                abs(level),
                1e-9,
            ) > 0.001:
                result.append(level)

        return result

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
                "support zones",
                "resistance zones",
                "nearest support",
                "nearest resistance",
                "support hold",
                "resistance test",
                "level break",
            ],
        }


def get_support_resistance_engine(
    provider=None,
) -> SupportResistanceEngine:
    return SupportResistanceEngine(
        provider=provider
    )


__all__ = [
    "SupportResistanceEngine",
    "get_support_resistance_engine",
]