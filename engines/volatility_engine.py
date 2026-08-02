from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

from engines.base_engine import BaseEngine, EngineResult


class VolatilityEngine(BaseEngine):

    NAME = "Volatility Engine"
    priority = 13
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

        atr = self._number(
            data.get("atr")
            or data.get("ATR")
        )

        atr_pct = self._number(
            data.get("atr_pct")
            or data.get("atr_percent")
        )

        if (
            atr_pct is None
            and atr is not None
            and price is not None
            and price > 0
        ):
            atr_pct = atr / price * 100.0

        volatility = self._number(
            data.get("volatility")
            or data.get("historical_volatility")
            or data.get("hv")
        )

        adx = self._number(
            data.get("adx")
            or data.get("ADX")
        )

        change_pct = self._number(
            data.get("change_pct")
            or data.get("price_change_pct")
        )

        direction = self._direction(
            atr_pct,
            volatility,
            adx,
            change_pct,
        )

        score = self._score(
            atr_pct,
            volatility,
            adx,
            change_pct,
        )

        reasons = self._reasons(
            atr_pct,
            volatility,
            adx,
            change_pct,
            direction,
        )

        warnings = self._warnings(
            price,
            atr,
            atr_pct,
        )

        quality = self._quality(
            price,
            atr,
            atr_pct,
            volatility,
            adx,
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
                "TRENDING",
                "HIGH_VOLATILITY_TREND",
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
                "atr": atr,
                "atr_pct": (
                    round(atr_pct, 3)
                    if atr_pct is not None
                    else None
                ),
                "historical_volatility": volatility,
                "adx": adx,
                "change_pct": change_pct,
                "data_quality": quality,
            },
        )

    def _direction(
        self,
        atr_pct: Optional[float],
        volatility: Optional[float],
        adx: Optional[float],
        change_pct: Optional[float],
    ) -> str:

        strong_trend = (
            adx is not None
            and adx >= 25
        )

        high_volatility = (
            atr_pct is not None
            and atr_pct >= 3.0
        )

        if strong_trend and high_volatility:
            return "HIGH_VOLATILITY_TREND"

        if strong_trend:
            return "TRENDING"

        if high_volatility:
            return "HIGH_VOLATILITY"

        if (
            atr_pct is not None
            and atr_pct <= 1.0
        ):
            return "LOW_VOLATILITY"

        if (
            volatility is not None
            and volatility >= 35
        ):
            return "HIGH_VOLATILITY"

        if (
            volatility is not None
            and volatility <= 15
        ):
            return "LOW_VOLATILITY"

        return "NORMAL"

    def _score(
        self,
        atr_pct: Optional[float],
        volatility: Optional[float],
        adx: Optional[float],
        change_pct: Optional[float],
    ) -> float:

        score = 50.0

        if adx is not None:
            if adx >= 35:
                score += 20
            elif adx >= 25:
                score += 12
            elif adx < 15:
                score -= 8

        if atr_pct is not None:
            if 1.0 <= atr_pct <= 4.0:
                score += 8
            elif atr_pct > 6.0:
                score -= 5
            elif atr_pct < 0.7:
                score -= 8

        if volatility is not None:
            if 15 <= volatility <= 35:
                score += 5
            elif volatility > 50:
                score -= 5

        if (
            change_pct is not None
            and adx is not None
            and adx >= 25
        ):
            if change_pct > 0:
                score += min(
                    10,
                    change_pct * 1.5,
                )
            elif change_pct < 0:
                score -= min(
                    10,
                    abs(change_pct) * 1.5,
                )

        return self._clamp(
            score,
            0,
            100,
        )

    def _reasons(
        self,
        atr_pct: Optional[float],
        volatility: Optional[float],
        adx: Optional[float],
        change_pct: Optional[float],
        direction: str,
    ) -> List[str]:

        reasons = []

        if direction == "HIGH_VOLATILITY_TREND":
            reasons.append(
                "Strong trend strength is accompanied by elevated volatility."
            )
        elif direction == "TRENDING":
            reasons.append(
                "ADX indicates a meaningful trend."
            )
        elif direction == "HIGH_VOLATILITY":
            reasons.append(
                "Volatility is elevated."
            )
        elif direction == "LOW_VOLATILITY":
            reasons.append(
                "Volatility is compressed."
            )
        else:
            reasons.append(
                "Volatility is within a normal range."
            )

        if (
            adx is not None
            and adx >= 25
        ):
            reasons.append(
                "ADX confirms trend strength."
            )

        if (
            atr_pct is not None
            and 1.0 <= atr_pct <= 4.0
        ):
            reasons.append(
                "ATR provides a usable trading range."
            )

        return self._dedupe(reasons)

    def _warnings(
        self,
        price: Optional[float],
        atr: Optional[float],
        atr_pct: Optional[float],
    ) -> List[str]:

        warnings = []

        if price is None:
            warnings.append(
                "Current price unavailable."
            )

        if atr is None:
            warnings.append(
                "ATR unavailable."
            )

        if atr_pct is None:
            warnings.append(
                "ATR percentage unavailable."
            )

        return warnings

    @staticmethod
    def _quality(
        price: Optional[float],
        atr: Optional[float],
        atr_pct: Optional[float],
        volatility: Optional[float],
        adx: Optional[float],
    ) -> str:

        count = sum(
            value is not None
            for value in (
                price,
                atr,
                atr_pct,
                volatility,
                adx,
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
                "ATR",
                "ATR percentage",
                "historical volatility",
                "ADX trend strength",
                "volatility regime",
            ],
        }


def get_volatility_engine(
    provider=None,
) -> VolatilityEngine:
    return VolatilityEngine(
        provider=provider
    )


__all__ = [
    "VolatilityEngine",
    "get_volatility_engine",
]