from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

from engines.base_engine import BaseEngine, EngineResult


class VWAPEngine(BaseEngine):

    NAME = "VWAP Engine"
    priority = 10
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

        vwap = self._number(
            data.get("vwap")
            or data.get("VWAP")
            or data.get("session_vwap")
        )

        previous_vwap = self._number(
            data.get("previous_vwap")
            or data.get("prior_vwap")
        )

        volume = self._number(
            data.get("volume")
        )

        volume_ma = self._number(
            data.get("volume_ma")
            or data.get("volume_average")
        )

        distance = self._distance(
            price,
            vwap,
        )

        direction = self._direction(
            price,
            vwap,
            previous_vwap,
        )

        score = self._score(
            price,
            vwap,
            previous_vwap,
            volume,
            volume_ma,
        )

        reasons = self._reasons(
            price,
            vwap,
            previous_vwap,
            volume,
            volume_ma,
            direction,
        )

        warnings = self._warnings(
            price,
            vwap,
            direction,
        )

        quality = self._quality(
            price,
            vwap,
            previous_vwap,
            volume,
            volume_ma,
        )

        confidence = {
            "HIGH": 85.0,
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
                "BULLISH",
                "STRONG_BULLISH",
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
                "vwap": vwap,
                "previous_vwap": previous_vwap,
                "distance_from_vwap_pct": (
                    round(distance, 3)
                    if distance is not None
                    else None
                ),
                "volume": volume,
                "volume_ma": volume_ma,
                "volume_ratio": (
                    round(
                        volume / volume_ma,
                        3,
                    )
                    if (
                        volume is not None
                        and volume_ma is not None
                        and volume_ma > 0
                    )
                    else None
                ),
                "data_quality": quality,
            },
        )

    def _direction(
        self,
        price: Optional[float],
        vwap: Optional[float],
        previous_vwap: Optional[float],
    ) -> str:

        if price is None or vwap is None:
            return "UNKNOWN"

        if previous_vwap is not None:
            if (
                price > vwap
                and vwap >= previous_vwap
            ):
                return "STRONG_BULLISH"

            if (
                price < vwap
                and vwap <= previous_vwap
            ):
                return "STRONG_BEARISH"

        if price > vwap:
            return "BULLISH"

        if price < vwap:
            return "BEARISH"

        return "NEUTRAL"

    def _score(
        self,
        price: Optional[float],
        vwap: Optional[float],
        previous_vwap: Optional[float],
        volume: Optional[float],
        volume_ma: Optional[float],
    ) -> float:

        if price is None or vwap is None:
            return 50.0

        distance = self._distance(
            price,
            vwap,
        ) or 0.0

        if price > vwap:
            score = min(
                78.0,
                58.0 + distance * 6.0,
            )

            if (
                previous_vwap is not None
                and vwap >= previous_vwap
            ):
                score += 8.0

            score += self._volume_bonus(
                volume,
                volume_ma,
            )

            return self._clamp(
                score,
                0,
                100,
            )

        if price < vwap:
            score = max(
                22.0,
                42.0 - distance * 6.0,
            )

            if (
                previous_vwap is not None
                and vwap <= previous_vwap
            ):
                score -= 8.0

            score -= self._volume_bonus(
                volume,
                volume_ma,
            )

            return self._clamp(
                score,
                0,
                100,
            )

        return 50.0

    def _volume_bonus(
        self,
        volume: Optional[float],
        volume_ma: Optional[float],
    ) -> float:

        if (
            volume is None
            or volume_ma is None
            or volume_ma <= 0
        ):
            return 0.0

        ratio = volume / volume_ma

        if ratio >= 2.0:
            return 12.0

        if ratio >= 1.5:
            return 9.0

        if ratio >= 1.25:
            return 6.0

        if ratio >= 1.1:
            return 3.0

        return 0.0

    def _reasons(
        self,
        price: Optional[float],
        vwap: Optional[float],
        previous_vwap: Optional[float],
        volume: Optional[float],
        volume_ma: Optional[float],
        direction: str,
    ) -> List[str]:

        reasons = []

        if direction == "STRONG_BULLISH":
            reasons.append(
                "Price is above VWAP and VWAP is rising."
            )
        elif direction == "BULLISH":
            reasons.append(
                "Price is trading above VWAP."
            )
        elif direction == "STRONG_BEARISH":
            reasons.append(
                "Price is below VWAP and VWAP is falling."
            )
        elif direction == "BEARISH":
            reasons.append(
                "Price is trading below VWAP."
            )
        elif direction == "NEUTRAL":
            reasons.append(
                "Price is at VWAP."
            )

        if (
            volume is not None
            and volume_ma is not None
            and volume_ma > 0
        ):
            ratio = volume / volume_ma

            if ratio >= 1.25:
                reasons.append(
                    "VWAP signal has above-average volume participation."
                )

        if (
            previous_vwap is not None
            and vwap is not None
            and vwap > previous_vwap
        ):
            reasons.append(
                "VWAP is trending upward."
            )

        return self._dedupe(reasons)

    def _warnings(
        self,
        price: Optional[float],
        vwap: Optional[float],
        direction: str,
    ) -> List[str]:

        warnings = []

        if price is None:
            warnings.append(
                "Current price unavailable."
            )

        if vwap is None:
            warnings.append(
                "VWAP unavailable."
            )

        if direction == "UNKNOWN":
            warnings.append(
                "Insufficient data for VWAP confirmation."
            )

        return warnings

    @staticmethod
    def _quality(
        price: Optional[float],
        vwap: Optional[float],
        previous_vwap: Optional[float],
        volume: Optional[float],
        volume_ma: Optional[float],
    ) -> str:

        count = sum(
            value is not None
            for value in (
                price,
                vwap,
                previous_vwap,
                volume,
                volume_ma,
            )
        )

        if count >= 4:
            return "HIGH"

        if count >= 2:
            return "MEDIUM"

        if count >= 1:
            return "LOW"

        return "NONE"

    @staticmethod
    def _distance(
        price: Optional[float],
        vwap: Optional[float],
    ) -> Optional[float]:

        if (
            price is None
            or vwap is None
            or vwap == 0
        ):
            return None

        return abs(
            price - vwap
        ) / abs(vwap) * 100.0

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
                "VWAP",
                "price versus VWAP",
                "VWAP trend",
                "volume confirmation",
                "intraday direction",
            ],
        }


def get_vwap_engine(
    provider=None,
) -> VWAPEngine:
    return VWAPEngine(
        provider=provider
    )


__all__ = [
    "VWAPEngine",
    "get_vwap_engine",
]