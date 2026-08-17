"""
TrendForge v2
Core Scanner

Pipeline:

Market Data
    ↓
Indicator Engine
    ↓
Scanner Rules
    ↓
Scoring Engine
    ↓
Signal Engine
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping

logger = logging.getLogger(__name__)


class Scanner:

    VERSION = "2.1"

    def __init__(
        self,
        data_provider: Any = None,
        indicator_engine: Any = None,
        rules: Any = None,
        scoring_engine: Any = None,
        signal_engine: Any = None,
        ranking_engine: Any = None,
    ) -> None:

        self.data_provider = data_provider
        self.indicator_engine = indicator_engine
        self.rules = rules
        self.scoring_engine = scoring_engine
        self.signal_engine = signal_engine
        self.ranking_engine = ranking_engine

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
            return obj.get(key, default)

        return getattr(obj, key, default)

    # =========================================================
    # DATA FETCH
    # =========================================================

    def fetch_data(
        self,
        symbol: str,
        timeframe: str | None = None,
    ) -> Any:

        if self.data_provider is None:
            raise RuntimeError(
                "Scanner requires a data provider"
            )

        for method_name in (
            "get_data",
            "fetch",
            "fetch_data",
            "historical_data",
            "get_historical_data",
        ):

            method = getattr(
                self.data_provider,
                method_name,
                None,
            )

            if not callable(method):
                continue

            try:
                return method(
                    symbol,
                    timeframe,
                )
            except TypeError:
                try:
                    return method(symbol)
                except TypeError:
                    continue

        raise AttributeError(
            "Data provider does not expose a supported "
            "data-fetch method"
        )

    # =========================================================
    # INDICATORS
    # =========================================================

    def calculate_indicators(
        self,
        data: Any,
    ) -> Any:

        if self.indicator_engine is None:
            return data

        for method_name in (
            "calculate",
            "calculate_indicators",
            "process",
            "run",
        ):

            method = getattr(
                self.indicator_engine,
                method_name,
                None,
            )

            if not callable(method):
                continue

            try:
                return method(data)
            except TypeError:
                continue

        return data

    # =========================================================
    # LATEST ROW
    # =========================================================

    @staticmethod
    def latest(
        data: Any,
    ) -> Any:

        if data is None:
            return None

        if hasattr(data, "empty"):

            if data.empty:
                return None

            return data.iloc[-1]

        return data

    # =========================================================
    # SCORE
    # =========================================================

    def calculate_score(
        self,
        latest: Any,
        fundamentals: Any = None,
    ) -> Any:

        if self.scoring_engine is None:
            return None

        method = getattr(
            self.scoring_engine,
            "score",
            None,
        )

        if not callable(method):
            return None

        attempts = (
            (
                latest,
                self.rules,
                fundamentals,
            ),
            (
                latest,
                fundamentals,
            ),
            (
                latest,
            ),
        )

        for args in attempts:

            try:
                return method(*args)
            except TypeError:
                continue

        return None

    # =========================================================
    # SIGNAL
    # =========================================================

    def generate_signal(
        self,
        score_result: Any,
        latest: Any,
        symbol: str,
        timeframe: str | None = None,
    ) -> Any:

        if self.signal_engine is None:
            return score_result

        method = getattr(
            self.signal_engine,
            "generate",
            None,
        )

        if not callable(method):
            return score_result

        return method(
            scoring_result=score_result,
            market_data=latest,
            symbol=symbol,
            timeframe=timeframe,
        )

    # =========================================================
    # SINGLE STOCK
    # =========================================================

    def scan_stock(
        self,
        symbol: str,
        timeframe: str | None = None,
        fundamentals: Any = None,
    ) -> dict[str, Any]:

        try:

            raw_data = self.fetch_data(
                symbol,
                timeframe,
            )

            if raw_data is None:
                return {
                    "symbol": symbol,
                    "status": "ERROR",
                    "error": "No market data",
                }

            indicator_data = (
                self.calculate_indicators(
                    raw_data
                )
            )

            latest = self.latest(
                indicator_data
            )

            if latest is None:
                return {
                    "symbol": symbol,
                    "status": "ERROR",
                    "error": "No indicator data",
                }

            score_result = (
                self.calculate_score(
                    latest,
                    fundamentals,
                )
            )

            signal_result = (
                self.generate_signal(
                    score_result,
                    latest,
                    symbol,
                    timeframe,
                )
                if score_result is not None
                else None
            )

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "status": "OK",

                "market_data": raw_data,

                "indicators": indicator_data,

                "latest": latest,

                "fundamentals": fundamentals,

                "score": score_result,

                "signal": signal_result,
            }

        except Exception as exc:

            logger.exception(
                "Scanner failed for %s",
                symbol,
            )

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "status": "ERROR",
                "error": str(exc),
            }

    # =========================================================
    # MULTI-STOCK SCAN
    # =========================================================

    def scan(
        self,
        symbols: Iterable[str],
        timeframe: str | None = None,
        fundamentals: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        symbols = list(symbols)

        results = []

        for symbol in symbols:

            stock_fundamentals = None

            if fundamentals is not None:

                stock_fundamentals = (
                    fundamentals.get(symbol)
                )

            result = self.scan_stock(
                symbol=symbol,
                timeframe=timeframe,
                fundamentals=stock_fundamentals,
            )

            results.append(result)

        # -----------------------------------------------------
        # RANK
        # -----------------------------------------------------

        if self.ranking_engine is not None:

            rank = getattr(
                self.ranking_engine,
                "rank",
                None,
            )

            if callable(rank):

                try:
                    results = rank(
                        results
                    )
                except Exception:

                    logger.exception(
                        "Ranking failed"
                    )

        return results

    # =========================================================
    # BUY SCAN
    # =========================================================

    def scan_buys(
        self,
        symbols: Iterable[str],
        timeframe: str | None = None,
        fundamentals: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        results = self.scan(
            symbols,
            timeframe,
            fundamentals,
        )

        output = []

        for result in results:

            signal = self._get(
                result,
                "signal",
            )

            signal_name = self._get(
                signal,
                "signal",
                "",
            )

            if str(
                signal_name
            ).upper() == "BUY":

                output.append(result)

        return output

    # =========================================================
    # SELL SCAN
    # =========================================================

    def scan_sells(
        self,
        symbols: Iterable[str],
        timeframe: str | None = None,
        fundamentals: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        results = self.scan(
            symbols,
            timeframe,
            fundamentals,
        )

        output = []

        for result in results:

            signal = self._get(
                result,
                "signal",
            )

            signal_name = self._get(
                signal,
                "signal",
                "",
            )

            if str(
                signal_name
            ).upper() == "SELL":

                output.append(result)

        return output

    # =========================================================
    # SUMMARY
    # =========================================================

    @classmethod
    def summary(
        cls,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:

        buy = 0
        sell = 0
        hold = 0
        errors = 0

        for result in results:

            if result.get(
                "status"
            ) == "ERROR":

                errors += 1
                continue

            signal = cls._get(
                result.get("signal"),
                "signal",
                "HOLD",
            )

            signal = str(
                signal
            ).upper()

            if signal == "BUY":
                buy += 1

            elif signal == "SELL":
                sell += 1

            else:
                hold += 1

        return {
            "total": len(results),
            "buy": buy,
            "sell": sell,
            "hold": hold,
            "errors": errors,
        }

    # =========================================================
    # HEALTH
    # =========================================================

    def health(self) -> dict[str, Any]:

        return {
            "status": "healthy",
            "version": self.VERSION,

            "data_provider": (
                self.data_provider is not None
            ),

            "indicator_engine": (
                self.indicator_engine is not None
            ),

            "rules": (
                self.rules is not None
            ),

            "scoring_engine": (
                self.scoring_engine is not None
            ),

            "signal_engine": (
                self.signal_engine is not None
            ),

            "ranking_engine": (
                self.ranking_engine is not None
            ),
        }