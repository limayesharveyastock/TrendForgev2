"""
TrendForge v2
Dashboard Service

Converts ranked pipeline results into dashboard-ready summaries.

Compatible with:
    Scanner
    Rules Engine
    Scoring Engine
    Signal Engine
    Ranking Engine
"""

from __future__ import annotations

from typing import Any, Mapping


class DashboardService:

    VERSION = "2.1"

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
    # SIGNAL EXTRACTION
    # =========================================================

    @classmethod
    def _signal(
        cls,
        result: Any,
    ) -> str:

        signal = cls._get(
            result,
            "signal",
        )

        # New pipeline structure:
        # result["signal"].signal

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

        # Direct structure

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
    # SCORE EXTRACTION
    # =========================================================

    @classmethod
    def _score(
        cls,
        result: Any,
    ) -> float:

        score = cls._get(
            result,
            "score",
        )

        if score is not None:

            value = cls._get(
                score,
                "total",
                None,
            )

            if value is not None:
                return cls._number(
                    score,
                    "total",
                )

        return cls._number(
            result,
            "overall_score",
            0.0,
        )

    # =========================================================
    # CONFIDENCE
    # =========================================================

    @classmethod
    def _confidence(
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

        score = cls._get(
            result,
            "score",
        )

        if score is not None:

            value = cls._get(
                score,
                "confidence",
                None,
            )

            if value is not None:

                return cls._number(
                    score,
                    "confidence",
                )

        return cls._number(
            result,
            "confidence",
            0.0,
        )

    # =========================================================
    # SYMBOL
    # =========================================================

    @classmethod
    def _symbol(
        cls,
        result: Any,
    ) -> str | None:

        value = cls._get(
            result,
            "symbol",
        )

        if value:
            return str(value)

        signal = cls._get(
            result,
            "signal",
        )

        value = cls._get(
            signal,
            "symbol",
        )

        if value:
            return str(value)

        return None

    # =========================================================
    # CATEGORIZE
    # =========================================================

    @classmethod
    def categorize(
        cls,
        results: list[Any],
    ) -> dict[str, list[Any]]:

        categories = {
            "strong_buy": [],
            "buy": [],
            "hold": [],
            "sell": [],
            "strong_sell": [],
            "error": [],
        }

        for result in results:

            if (
                cls._get(
                    result,
                    "status",
                )
                == "ERROR"
            ):

                categories[
                    "error"
                ].append(result)

                continue

            signal = cls._signal(
                result
            )

            confidence = cls._confidence(
                result
            )

            if signal == "BUY":

                if confidence >= 80:
                    categories[
                        "strong_buy"
                    ].append(result)
                else:
                    categories[
                        "buy"
                    ].append(result)

            elif signal == "SELL":

                if confidence >= 80:
                    categories[
                        "strong_sell"
                    ].append(result)
                else:
                    categories[
                        "sell"
                    ].append(result)

            else:

                categories[
                    "hold"
                ].append(result)

        return categories

    # =========================================================
    # AVERAGES
    # =========================================================

    @classmethod
    def average_score(
        cls,
        results: list[Any],
    ) -> float:

        if not results:
            return 0.0

        values = [
            cls._score(
                result
            )
            for result in results
        ]

        return round(
            sum(values)
            / len(values),
            2,
        )

    @classmethod
    def average_confidence(
        cls,
        results: list[Any],
    ) -> float:

        if not results:
            return 0.0

        values = [
            cls._confidence(
                result
            )
            for result in results
        ]

        return round(
            sum(values)
            / len(values),
            2,
        )

    # =========================================================
    # TOP PICKS
    # =========================================================

    @classmethod
    def top_picks(
        cls,
        results: list[Any],
        limit: int = 10,
    ) -> list[dict[str, Any]]:

        ranked = sorted(
            results,
            key=lambda item: (
                cls._score(item),
                cls._confidence(item),
            ),
            reverse=True,
        )

        output = []

        for result in ranked[:limit]:

            output.append(
                {
                    "symbol": cls._symbol(
                        result
                    ),
                    "signal": cls._signal(
                        result
                    ),
                    "score": round(
                        cls._score(result),
                        2,
                    ),
                    "confidence": round(
                        cls._confidence(result),
                        2,
                    ),
                }
            )

        return output

    # =========================================================
    # BUY LIST
    # =========================================================

    @classmethod
    def buy_list(
        cls,
        results: list[Any],
        limit: int = 10,
    ) -> list[dict[str, Any]]:

        buys = [
            result
            for result in results
            if cls._signal(result)
            == "BUY"
        ]

        buys.sort(
            key=lambda item: (
                cls._confidence(item),
                cls._score(item),
            ),
            reverse=True,
        )

        return cls.top_picks(
            buys,
            limit,
        )

    # =========================================================
    # SELL LIST
    # =========================================================

    @classmethod
    def sell_list(
        cls,
        results: list[Any],
        limit: int = 10,
    ) -> list[dict[str, Any]]:

        sells = [
            result
            for result in results
            if cls._signal(result)
            == "SELL"
        ]

        sells.sort(
            key=lambda item: (
                cls._confidence(item),
                abs(cls._score(item)),
            ),
            reverse=True,
        )

        return cls.top_picks(
            sells,
            limit,
        )

    # =========================================================
    # MASTER BUILD
    # =========================================================

    @classmethod
    def build(
        cls,
        signals: list[Any],
    ) -> dict[str, Any]:

        signals = list(
            signals or []
        )

        categories = cls.categorize(
            signals
        )

        return {
            "version": cls.VERSION,

            "total": len(signals),

            "strong_buy": len(
                categories[
                    "strong_buy"
                ]
            ),

            "buy": len(
                categories[
                    "buy"
                ]
            ),

            "hold": len(
                categories[
                    "hold"
                ]
            ),

            "sell": len(
                categories[
                    "sell"
                ]
            ),

            "strong_sell": len(
                categories[
                    "strong_sell"
                ]
            ),

            "errors": len(
                categories[
                    "error"
                ]
            ),

            "average_score": cls.average_score(
                signals
            ),

            "average_confidence": cls.average_confidence(
                signals
            ),

            "top_picks": cls.top_picks(
                signals
            ),

            "top_buys": cls.buy_list(
                signals
            ),

            "top_sells": cls.sell_list(
                signals
            ),
        }

    # =========================================================
    # DASHBOARD TABLE
    # =========================================================

    @classmethod
    def table_rows(
        cls,
        signals: list[Any],
    ) -> list[dict[str, Any]]:

        rows = []

        for result in signals:

            rows.append(
                {
                    "symbol": cls._symbol(
                        result
                    ),
                    "signal": cls._signal(
                        result
                    ),
                    "score": round(
                        cls._score(result),
                        2,
                    ),
                    "confidence": round(
                        cls._confidence(result),
                        2,
                    ),
                    "status": cls._get(
                        result,
                        "status",
                        "OK",
                    ),
                }
            )

        return rows

    # =========================================================
    # HEALTH
    # =========================================================

    @classmethod
    def health(cls) -> dict[str, Any]:

        return {
            "status": "healthy",
            "version": cls.VERSION,
        }