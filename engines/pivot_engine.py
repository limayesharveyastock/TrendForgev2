from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

from engines.base_engine import BaseEngine, EngineResult


class PivotEngine(BaseEngine):

    NAME = "Pivot Engine"
    priority = 9
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

        high = self._number(data.get("high"))
        low = self._number(data.get("low"))
        close = self._number(
            data.get("close")
            or data.get("ltp")
            or data.get("price")
        )

        pivot = self._number(
            data.get("pivot")
            or data.get("pivot_point")
        )

        r1 = self._number(
            data.get("r1")
            or data.get("resistance_1")
        )

        r2 = self._number(
            data.get("r2")
            or data.get("resistance_2")
        )

        r3 = self._number(
            data.get("r3")
            or data.get("resistance_3")
        )

        s1 = self._number(
            data.get("s1")
            or data.get("support_1")
        )

        s2 = self._number(
            data.get("s2")
            or data.get("support_2")
        )

        s3 = self._number(
            data.get("s3")
            or data.get("support_3")
        )

        if pivot is None and None not in (
            high,
            low,
            close,
        ):
            pivot = (high + low + close) / 3.0

        if None not in (
            high,
            low,
            close,
            pivot,
        ):
            if r1 is None:
                r1 = 2 * pivot - low

            if s1 is None:
                s1 = 2 * pivot - high

            if r2 is None:
                r2 = pivot + (high - low)

            if s2 is None:
                s2 = pivot - (high - low)

            if r3 is None:
                r3 = high + 2 * (pivot - low)

            if s3 is None:
                s3 = low - 2 * (high - pivot)

        direction = self._direction(
            close,
            pivot,
            r1,
            r2,
            s1,
            s2,
        )

        score = self._score(
            close,
            pivot,
            r1,
            r2,
            s1,
            s2,
        )

        distance = self._nearest_distance(
            close,
            direction,
            r1,
            r2,
            s1,
            s2,
        )

        reasons = self._reasons(
            close,
            pivot,
            r1,
            r2,
            s1,
            s2,
            direction,
        )

        warnings = self._warnings(
            close,
            pivot,
            direction,
        )

        quality = self._quality(
            high,
            low,
            close,
            pivot,
            r1,
            s1,
        )

        confidence = {
            "HIGH": 82.0,
            "MEDIUM": 65.0,
            "LOW": 42.0,
            "NONE": 15.0,
        }.get(
            quality,
            15.0,
        )

        return EngineResult(
            engine=self.NAME,
            passed=direction in (
                "BULLISH",
                "STRONG_BULLISH",
            ),
            score=round(score, 2),
            confidence=round(confidence, 2),
            grade=self._grade(score),
            reasons=reasons,
            warnings=warnings,
            metrics={
                "symbol": symbol,
                "direction": direction,
                "high": high,
                "low": low,
                "close": close,
                "pivot": pivot,
                "r1": r1,
                "r2": r2,
                "r3": r3,
                "s1": s1,
                "s2": s2,
                "s3": s3,
                "nearest_level_distance_pct": (
                    round(distance, 3)
                    if distance is not None
                    else None
                ),
                "data_quality": quality,
            },
        )

    def _direction(
        self,
        close: Optional[float],
        pivot: Optional[float],
        r1: Optional[float],
        r2: Optional[float],
        s1: Optional[float],
        s2: Optional[float],
    ) -> str:

        if close is None or pivot is None:
            return "UNKNOWN"

        if r2 is not None and close >= r2:
            return "STRONG_BULLISH"

        if r1 is not None and close >= r1:
            return "BULLISH"

        if close > pivot:
            return "BULLISH"

        if s2 is not None and close <= s2:
            return "STRONG_BEARISH"

        if s1 is not None and close <= s1:
            return "BEARISH"

        if close < pivot:
            return "BEARISH"

        return "NEUTRAL"

    def _score(
        self,
        close: Optional[float],
        pivot: Optional[float],
        r1: Optional[float],
        r2: Optional[float],
        s1: Optional[float],
        s2: Optional[float],
    ) -> float:

        if close is None or pivot is None:
            return 50.0

        if r2 is not None and close >= r2:
            return 92.0

        if r1 is not None and close >= r1:
            return 80.0

        if close > pivot:
            distance = self._relative_distance(
                close,
                pivot,
            )
            return min(
                75.0,
                60.0 + distance * 5.0,
            )

        if s2 is not None and close <= s2:
            return 8.0

        if s1 is not None and close <= s1:
            return 20.0

        distance = self._relative_distance(
            close,
            pivot,
        )

        return max(
            25.0,
            50.0 - distance * 5.0,
        )

    def _nearest_distance(
        self,
        close: Optional[float],
        direction: str,
        r1: Optional[float],
        r2: Optional[float],
        s1: Optional[float],
        s2: Optional[float],
    ) -> Optional[float]:

        if close is None:
            return None

        levels = []

        if direction in (
            "BULLISH",
            "STRONG_BULLISH",
        ):
            levels = [
                value
                for value in (
                    r1,
                    r2,
                )
                if value is not None
            ]
        elif direction in (
            "BEARISH",
            "STRONG_BEARISH",
        ):
            levels = [
                value
                for value in (
                    s1,
                    s2,
                )
                if value is not None
            ]
        else:
            levels = [
                value
                for value in (
                    r1,
                    s1,
                )
                if value is not None
            ]

        if not levels:
            return None

        return min(
            (
                abs(close - level)
                / abs(level)
                * 100
                for level in levels
                if level != 0
            ),
            default=None,
        )

    def _reasons(
        self,
        close: Optional[float],
        pivot: Optional[float],
        r1: Optional[float],
        r2: Optional[float],
        s1: Optional[float],
        s2: Optional[float],
        direction: str,
    ) -> List[str]:

        reasons = []

        if direction == "STRONG_BULLISH":
            reasons.append(
                "Price is above the second resistance pivot level."
            )
        elif direction == "BULLISH":
            reasons.append(
                "Price is trading above the central pivot."
            )
        elif direction == "STRONG_BEARISH":
            reasons.append(
                "Price is below the second support pivot level."
            )
        elif direction == "BEARISH":
            reasons.append(
                "Price is trading below the central pivot."
            )
        elif direction == "NEUTRAL":
            reasons.append(
                "Price is near the central pivot."
            )

        if (
            close is not None
            and r1 is not None
            and close >= r1
        ):
            reasons.append(
                "R1 has been reclaimed."
            )

        if (
            close is not None
            and s1 is not None
            and close <= s1
        ):
            reasons.append(
                "S1 has been lost."
            )

        return self._dedupe(reasons)

    def _warnings(
        self,
        close: Optional[float],
        pivot: Optional[float],
        direction: str,
    ) -> List[str]:

        warnings = []

        if close is None:
            warnings.append(
                "Current price unavailable."
            )

        if pivot is None:
            warnings.append(
                "Pivot level unavailable."
            )

        if direction == "UNKNOWN":
            warnings.append(
                "Insufficient pivot data for directional confirmation."
            )

        return warnings

    @staticmethod
    def _quality(
        high: Optional[float],
        low: Optional[float],
        close: Optional[float],
        pivot: Optional[float],
        r1: Optional[float],
        s1: Optional[float],
    ) -> str:

        count = sum(
            value is not None
            for value in (
                high,
                low,
                close,
                pivot,
                r1,
                s1,
            )
        )

        if count >= 5:
            return "HIGH"

        if count >= 3:
            return "MEDIUM"

        if count >= 1:
            return "LOW"

        return "NONE"

    @staticmethod
    def _relative_distance(
        first: float,
        second: float,
    ) -> float:

        if second == 0:
            return 0.0

        return abs(
            first - second
        ) / abs(second) * 100.0

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
                "pivot point",
                "R1",
                "R2",
                "R3",
                "S1",
                "S2",
                "S3",
                "pivot direction",
            ],
        }


def get_pivot_engine(
    provider=None,
) -> PivotEngine:
    return PivotEngine(
        provider=provider
    )


__all__ = [
    "PivotEngine",
    "get_pivot_engine",
]