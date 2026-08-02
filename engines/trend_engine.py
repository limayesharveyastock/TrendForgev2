from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

from engines.base_engine import BaseEngine, EngineResult


class TrendEngine(BaseEngine):

    NAME = "Trend Engine"
    priority = 14
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

        ema9 = self._number(
            data.get("ema9")
            or data.get("ema_9")
        )
        ema20 = self._number(
            data.get("ema20")
            or data.get("ema_20")
        )
        ema26 = self._number(
            data.get("ema26")
            or data.get("ema_26")
        )
        ema50 = self._number(
            data.get("ema50")
            or data.get("ema_50")
        )
        ema100 = self._number(
            data.get("ema100")
            or data.get("ema_100")
        )
        ema200 = self._number(
            data.get("ema200")
            or data.get("ema_200")
        )

        vwma9 = self._number(
            data.get("vwma9")
            or data.get("vwma_9")
        )
        vwma26 = self._number(
            data.get("vwma26")
            or data.get("vwma_26")
        )

        adx = self._number(
            data.get("adx")
            or data.get("ADX")
        )

        trend_value = self._number(
            data.get("trend_score")
            or data.get("trend_strength")
        )

        bullish = 0
        bearish = 0
        total = 0
        reasons: List[str] = []
        warnings: List[str] = []

        pairs = [
            ("EMA9", ema9, ema26),
            ("EMA20", ema20, ema50),
            ("EMA50", ema50, ema200),
            ("VWMA9", vwma9, vwma26),
        ]

        for name, fast, slow in pairs:
            if fast is None or slow is None:
                continue

            total += 1

            if fast > slow:
                bullish += 1
                reasons.append(
                    f"{name} fast line is above the slower line."
                )
            elif fast < slow:
                bearish += 1

        if price is not None:
            for name, average in (
                ("EMA9", ema9),
                ("EMA20", ema20),
                ("EMA50", ema50),
                ("EMA100", ema100),
                ("EMA200", ema200),
                ("VWMA9", vwma9),
                ("VWMA26", vwma26),
            ):
                if average is None:
                    continue

                total += 1

                if price > average:
                    bullish += 1
                elif price < average:
                    bearish += 1

        score = self._score(
            bullish,
            bearish,
            total,
            adx,
            trend_value,
        )

        direction = self._direction(
            bullish,
            bearish,
            total,
            adx,
        )

        if direction == "STRONG_BULLISH":
            reasons.append(
                "Trend structure is strongly bullish."
            )
        elif direction == "BULLISH":
            reasons.append(
                "Trend structure is bullish."
            )
        elif direction == "STRONG_BEARISH":
            reasons.append(
                "Trend structure is strongly bearish."
            )
        elif direction == "BEARISH":
            reasons.append(
                "Trend structure is bearish."
            )
        elif direction == "MIXED":
            warnings.append(
                "Trend signals are mixed."
            )
        else:
            warnings.append(
                "Insufficient trend data."
            )

        if adx is not None:
            if adx >= 25:
                reasons.append(
                    "ADX confirms meaningful trend strength."
                )
            elif adx < 15:
                warnings.append(
                    "ADX indicates weak trend strength."
                )

        quality = self._quality(
            price,
            ema9,
            ema26,
            ema50,
            ema200,
            vwma9,
            vwma26,
            adx,
        )

        confidence = {
            "HIGH": 86.0,
            "MEDIUM": 68.0,
            "LOW": 44.0,
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
                "ema9": ema9,
                "ema20": ema20,
                "ema26": ema26,
                "ema50": ema50,
                "ema100": ema100,
                "ema200": ema200,
                "vwma9": vwma9,
                "vwma26": vwma26,
                "adx": adx,
                "trend_value": trend_value,
                "bullish_components": bullish,
                "bearish_components": bearish,
                "total_components": total,
                "data_quality": quality,
            },
        )

    @staticmethod
    def _direction(
        bullish: int,
        bearish: int,
        total: int,
        adx: Optional[float],
    ) -> str:

        if total == 0:
            return "UNKNOWN"

        bull_ratio = bullish / total
        bear_ratio = bearish / total

        strong = (
            adx is not None
            and adx >= 25
        )

        if bull_ratio >= 0.75:
            return "STRONG_BULLISH" if strong else "BULLISH"

        if bear_ratio >= 0.75:
            return "STRONG_BEARISH" if strong else "BEARISH"

        if bull_ratio > 0.55:
            return "BULLISH"

        if bear_ratio > 0.55:
            return "BEARISH"

        return "MIXED"

    @staticmethod
    def _score(
        bullish: int,
        bearish: int,
        total: int,
        adx: Optional[float],
        trend_value: Optional[float],
    ) -> float:

        if total == 0:
            return 50.0

        score = 50.0
        net_ratio = (bullish - bearish) / total

        score += net_ratio * 40.0

        if adx is not None:
            if adx >= 35:
                score += 8.0 if net_ratio > 0 else -8.0
            elif adx >= 25:
                score += 5.0 if net_ratio > 0 else -5.0
            elif adx < 15:
                score *= 0.95

        if trend_value is not None:
            if 0 <= trend_value <= 100:
                score = (
                    score * 0.7
                    + trend_value * 0.3
                )

        return max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

    @staticmethod
    def _quality(
        price: Optional[float],
        ema9: Optional[float],
        ema26: Optional[float],
        ema50: Optional[float],
        ema200: Optional[float],
        vwma9: Optional[float],
        vwma26: Optional[float],
        adx: Optional[float],
    ) -> str:

        count = sum(
            value is not None
            for value in (
                price,
                ema9,
                ema26,
                ema50,
                ema200,
                vwma9,
                vwma26,
                adx,
            )
        )

        if count >= 6:
            return "HIGH"

        if count >= 3:
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
                "EMA trend structure",
                "VWMA trend structure",
                "price versus moving averages",
                "ADX trend strength",
                "multi-average alignment",
            ],
        }


def get_trend_engine(
    provider=None,
) -> TrendEngine:
    return TrendEngine(
        provider=provider
    )


__all__ = [
    "TrendEngine",
    "get_trend_engine",
]