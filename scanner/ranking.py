"""
TrendForge v2
Ranking Engine

Ranks scanner results using the unified TrendForge
Scoring Engine + Signal Engine outputs.
"""

from __future__ import annotations

from typing import Any, Mapping


class RankingEngine:

    VERSION = "2.1"

    SIGNAL_PRIORITY = {
        "BUY": 3,
        "SELL": 2,
        "HOLD": 1,
    }

    # =========================================================
    # SAFE ACCESS
    # =========================================================

    @staticmethod
    def _get(
        obj: Any,
        key: str,
        default: Any = None,
    ) -> Any:

        if obj is None:
            return default

        if isinstance(obj, Mapping):
            return obj.get(
                key,
                default,
            )

        return getattr(
            obj,
            key,
            default,
        )

    @classmethod
    def _number(
        cls,
        obj: Any,
        key: str,
        default: float = 0.0,
    ) -> float:

        value = cls._get(
            obj,
            key,
            default,
        )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return default

    # =========================================================
    # EXTRACT SCORE
    # =========================================================

    @classmethod
    def score(
        cls,
        result: Any,
    ) -> float:

        # New pipeline:
        # result["score"].total

        scoring = cls._get(
            result,
            "score",
        )

        if scoring is not None:

            value = cls._get(
                scoring,
                "total",
                None,
            )

            if value is not None:

                return cls._number(
                    scoring,
                    "total",
                )

        # Backward compatibility

        return cls._number(
            result,
            "overall_score",
            cls._number(
                result,
                "score",
                0.0,
            ),
        )

    # =========================================================
    # EXTRACT CONFIDENCE
    # =========================================================

    @classmethod
    def confidence(
        cls,
        result: Any,
    ) -> float:

        signal = cls._get(
            result,
            "signal",
        )

        if signal is not None:

            value = cls._get(
                signal,
                "confidence",
                None,
            )

            if value is not None:

                return cls._number(
                    signal,
                    "confidence",
                )

        scoring = cls._get(
            result,
            "score",
        )

        if scoring is not None:

            value = cls._get(
                scoring,
                "confidence",
                None,
            )

            if value is not None:

                return cls._number(
                    scoring,
                    "confidence",
                )

        return cls._number(
            result,
            "confidence",
            0.0,
        )

    # =========================================================
    # EXTRACT SIGNAL
    # =========================================================

    @classmethod
    def signal(
        cls,
        result: Any,
    ) -> str:

        signal = cls._get(
            result,
            "signal",
        )

        if signal is not None:

            value = cls._get(
                signal,
                "signal",
                None,
            )

            if value:
                return str(
                    value
                ).upper()

        value = cls._get(
            result,
            "signal_type",
            cls._get(
                result,
                "action",
                "HOLD",
            ),
        )

        return str(
            value
        ).upper()

    # =========================================================
    # RANK KEY
    # =========================================================

    @classmethod
    def rank_key(
        cls,
        result: Any,
    ) -> tuple:

        signal = cls.signal(
            result
        )

        score = cls.score(
            result
        )

        confidence = cls.confidence(
            result
        )

        priority = cls.SIGNAL_PRIORITY.get(
            signal,
            0,
        )

        # Score first.
        # Confidence second.
        # Signal priority third.

        return (
            score,
            confidence,
            priority,
        )

    # =========================================================
    # RANK
    # =========================================================

    @classmethod
    def rank(
        cls,
        signals: list[Any],
    ) -> list[Any]:

        if not signals:
            return []

        valid = [
            item
            for item in signals
            if item is not None
        ]

        return sorted(
            valid,
            key=cls.rank_key,
            reverse=True,
        )

    # =========================================================
    # FILTER
    # =========================================================

    @classmethod
    def filter_signal(
        cls,
        signals: list[Any],
        signal: str,
    ) -> list[Any]:

        signal = signal.upper()

        return [
            item
            for item in signals
            if cls.signal(item)
            == signal
        ]

    @classmethod
    def buys(
        cls,
        signals: list[Any],
    ) -> list[Any]:

        return cls.filter_signal(
            signals,
            "BUY",
        )

    @classmethod
    def sells(
        cls,
        signals: list[Any],
    ) -> list[Any]:

        return cls.filter_signal(
            signals,
            "SELL",
        )

    @classmethod
    def holds(
        cls,
        signals: list[Any],
    ) -> list[Any]:

        return cls.filter_signal(
            signals,
            "HOLD",
        )

    # =========================================================
    # TOP SIGNALS
    # =========================================================

    @classmethod
    def top(
        cls,
        signals: list[Any],
        limit: int = 10,
    ) -> list[Any]:

        if limit <= 0:
            return []

        return cls.rank(
            signals
        )[:limit]

    @classmethod
    def top_buys(
        cls,
        signals: list[Any],
        limit: int = 10,
    ) -> list[Any]:

        return cls.top(
            cls.buys(signals),
            limit,
        )

    @classmethod
    def top_sells(
        cls,
        signals: list[Any],
        limit: int = 10,
    ) -> list[Any]:

        return cls.top(
            cls.sells(signals),
            limit,
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    @classmethod
    def summary(
        cls,
        signals: list[Any],
    ) -> dict[str, Any]:

        ranked = cls.rank(
            signals
        )

        buys = cls.buys(
            ranked
        )

        sells = cls.sells(
            ranked
        )

        holds = cls.holds(
            ranked
        )

        return {
            "total": len(ranked),
            "buy": len(buys),
            "sell": len(sells),
            "hold": len(holds),
            "top_buy": (
                cls._get(
                    buys[0],
                    "symbol",
                )
                if buys
                else None
            ),
            "top_sell": (
                cls._get(
                    sells[0],
                    "symbol",
                )
                if sells
                else None
            ),
        }

    # =========================================================
    # HEALTH
    # =========================================================

    @classmethod
    def health(cls) -> dict[str, Any]:

        return {
            "status": "healthy",
            "version": cls.VERSION,
            "signal_priority": dict(
                cls.SIGNAL_PRIORITY
            ),
        }