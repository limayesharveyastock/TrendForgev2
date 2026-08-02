from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

from engines.base_engine import BaseEngine, EngineResult


class VolumeEngine(BaseEngine):

    NAME = "Volume Engine"
    priority = 11
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

        volume = self._number(
            data.get("volume")
        )

        volume_ma = self._number(
            data.get("volume_ma")
            or data.get("volume_average")
            or data.get("avg_volume")
        )

        volume_ma_20 = self._number(
            data.get("volume_ma_20")
            or data.get("avg_volume_20")
        )

        volume_ma = (
            volume_ma
            if volume_ma is not None
            else volume_ma_20
        )

        ratio = self._number(
            data.get("volume_ratio")
            or data.get("rvol")
            or data.get("relative_volume")
        )

        if (
            ratio is None
            and volume is not None
            and volume_ma is not None
            and volume_ma > 0
        ):
            ratio = volume / volume_ma

        price_change = self._number(
            data.get("change_pct")
            or data.get("price_change_pct")
            or data.get("return_pct")
        )

        buy_volume = self._number(
            data.get("buy_volume")
        )

        sell_volume = self._number(
            data.get("sell_volume")
        )

        direction = self._direction(
            ratio,
            price_change,
            buy_volume,
            sell_volume,
        )

        score = self._score(
            ratio,
            price_change,
            buy_volume,
            sell_volume,
        )

        reasons = self._reasons(
            ratio,
            price_change,
            buy_volume,
            sell_volume,
            direction,
        )

        warnings = self._warnings(
            volume,
            volume_ma,
            ratio,
        )

        quality = self._quality(
            volume,
            volume_ma,
            ratio,
            price_change,
        )

        confidence = {
            "HIGH": 84.0,
            "MEDIUM": 67.0,
            "LOW": 43.0,
            "NONE": 15.0,
        }.get(
            quality,
            15.0,
        )

        return EngineResult(
            engine=self.NAME,
            passed=direction in (
                "STRONG_ACCUMULATION",
                "ACCUMULATION",
            ),
            score=round(score, 2),
            confidence=round(confidence, 2),
            grade=self._grade(score),
            reasons=self._dedupe(reasons),
            warnings=self._dedupe(warnings),
            metrics={
                "symbol": symbol,
                "direction": direction,
                "volume": volume,
                "volume_ma": volume_ma,
                "volume_ratio": (
                    round(ratio, 3)
                    if ratio is not None
                    else None
                ),
                "price_change_pct": price_change,
                "buy_volume": buy_volume,
                "sell_volume": sell_volume,
                "buy_sell_ratio": self._buy_sell_ratio(
                    buy_volume,
                    sell_volume,
                ),
                "data_quality": quality,
            },
        )

    def _direction(
        self,
        ratio: Optional[float],
        price_change: Optional[float],
        buy_volume: Optional[float],
        sell_volume: Optional[float],
    ) -> str:

        if (
            buy_volume is not None
            and sell_volume is not None
            and buy_volume + sell_volume > 0
        ):
            buy_ratio = (
                buy_volume
                / (buy_volume + sell_volume)
            )

            if buy_ratio >= 0.65:
                return "STRONG_ACCUMULATION"

            if buy_ratio >= 0.55:
                return "ACCUMULATION"

            if buy_ratio <= 0.35:
                return "STRONG_DISTRIBUTION"

            if buy_ratio <= 0.45:
                return "DISTRIBUTION"

        if ratio is None:
            return "UNKNOWN"

        if ratio >= 1.5:
            if price_change is not None:
                if price_change > 0:
                    return "STRONG_ACCUMULATION"
                if price_change < 0:
                    return "STRONG_DISTRIBUTION"

            return "HIGH_ACTIVITY"

        if ratio >= 1.2:
            if price_change is not None:
                if price_change > 0:
                    return "ACCUMULATION"
                if price_change < 0:
                    return "DISTRIBUTION"

            return "HIGH_ACTIVITY"

        if ratio < 0.8:
            return "LOW_ACTIVITY"

        return "NORMAL"

    def _score(
        self,
        ratio: Optional[float],
        price_change: Optional[float],
        buy_volume: Optional[float],
        sell_volume: Optional[float],
    ) -> float:

        score = 50.0

        if ratio is not None:
            if ratio >= 2.0:
                score += 20
            elif ratio >= 1.5:
                score += 15
            elif ratio >= 1.25:
                score += 10
            elif ratio >= 1.1:
                score += 5
            elif ratio < 0.7:
                score -= 12
            elif ratio < 0.85:
                score -= 6

        if price_change is not None and ratio is not None:
            if ratio >= 1.2:
                if price_change > 0:
                    score += min(
                        12,
                        price_change * 2,
                    )
                elif price_change < 0:
                    score -= min(
                        12,
                        abs(price_change) * 2,
                    )

        if (
            buy_volume is not None
            and sell_volume is not None
            and buy_volume + sell_volume > 0
        ):
            buy_ratio = (
                buy_volume
                / (buy_volume + sell_volume)
            )

            score += (
                buy_ratio - 0.5
            ) * 30

        return self._clamp(
            score,
            0,
            100,
        )

    def _reasons(
        self,
        ratio: Optional[float],
        price_change: Optional[float],
        buy_volume: Optional[float],
        sell_volume: Optional[float],
        direction: str,
    ) -> List[str]:

        reasons = []

        if direction == "STRONG_ACCUMULATION":
            reasons.append(
                "Strong volume-backed accumulation detected."
            )
        elif direction == "ACCUMULATION":
            reasons.append(
                "Volume supports accumulation."
            )
        elif direction == "STRONG_DISTRIBUTION":
            reasons.append(
                "Strong volume-backed distribution detected."
            )
        elif direction == "DISTRIBUTION":
            reasons.append(
                "Volume supports distribution."
            )
        elif direction == "HIGH_ACTIVITY":
            reasons.append(
                "Trading volume is significantly above average."
            )
        elif direction == "LOW_ACTIVITY":
            reasons.append(
                "Trading volume is below average."
            )

        if ratio is not None:
            if ratio >= 2.0:
                reasons.append(
                    "Volume is at least 2x its reference average."
                )
            elif ratio >= 1.5:
                reasons.append(
                    "Volume is materially above average."
                )

        if (
            price_change is not None
            and ratio is not None
            and ratio >= 1.2
        ):
            if price_change > 0:
                reasons.append(
                    "Price is rising with above-average volume."
                )
            elif price_change < 0:
                reasons.append(
                    "Price is falling with above-average volume."
                )

        return self._dedupe(reasons)

    def _warnings(
        self,
        volume: Optional[float],
        volume_ma: Optional[float],
        ratio: Optional[float],
    ) -> List[str]:

        warnings = []

        if volume is None:
            warnings.append(
                "Current volume unavailable."
            )

        if volume_ma is None:
            warnings.append(
                "Volume average unavailable."
            )

        if ratio is None:
            warnings.append(
                "Relative volume cannot be calculated."
            )

        return warnings

    @staticmethod
    def _quality(
        volume: Optional[float],
        volume_ma: Optional[float],
        ratio: Optional[float],
        price_change: Optional[float],
    ) -> str:

        count = sum(
            value is not None
            for value in (
                volume,
                volume_ma,
                ratio,
                price_change,
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
    def _buy_sell_ratio(
        buy_volume: Optional[float],
        sell_volume: Optional[float],
    ) -> Optional[float]:

        if (
            buy_volume is None
            or sell_volume is None
            or sell_volume <= 0
        ):
            return None

        return round(
            buy_volume / sell_volume,
            3,
        )

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
                "volume versus average",
                "relative volume",
                "volume-price confirmation",
                "buy volume",
                "sell volume",
                "accumulation",
                "distribution",
            ],
        }


def get_volume_engine(
    provider=None,
) -> VolumeEngine:
    return VolumeEngine(
        provider=provider
    )


__all__ = [
    "VolumeEngine",
    "get_volume_engine",
]