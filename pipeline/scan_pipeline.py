"""
TrendForge v2
Scan Pipeline

Orchestration layer:

Market Data
    ↓
Indicators
    ↓
Rules
    ↓
Scoring
    ↓
Signals
    ↓
Ranking
    ↓
Dashboard
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping

logger = logging.getLogger(__name__)


class ScanPipeline:

    VERSION = "2.1"

    def __init__(
        self,
        scanner: Any = None,
        ranking: Any = None,
        dashboard: Any = None,
        indicator_engine: Any = None,
        rules: Any = None,
        scoring_engine: Any = None,
        signal_engine: Any = None,
    ) -> None:

        self.scanner = scanner
        self.ranking = ranking
        self.dashboard = dashboard

        self.indicator_engine = indicator_engine
        self.rules = rules
        self.scoring_engine = scoring_engine
        self.signal_engine = signal_engine

    # =========================================================
    # SAFE CALL
    # =========================================================

    @staticmethod
    def _call(
        obj: Any,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        if obj is None:
            return None

        function = getattr(
            obj,
            method,
            None,
        )

        if not callable(function):
            return None

        try:
            return function(
                *args,
                **kwargs,
            )
        except TypeError:
            return function(*args)

    # =========================================================
    # SCANNER
    # =========================================================

    def scan_symbols(
        self,
        symbols: Iterable[str],
        capital: float | None = None,
    ) -> Any:

        if self.scanner is None:
            raise RuntimeError(
                "ScanPipeline requires a scanner"
            )

        symbols = list(symbols)

        scan = getattr(
            self.scanner,
            "scan",
            None,
        )

        if not callable(scan):
            raise AttributeError(
                "Scanner does not expose scan()"
            )

        try:
            return scan(
                symbols,
                capital,
            )
        except TypeError:
            return scan(symbols)

    # =========================================================
    # INDICATOR PROCESSING
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

            if callable(method):

                try:
                    return method(data)
                except TypeError:
                    continue

        return data

    # =========================================================
    # SINGLE STOCK
    # =========================================================

    def process_stock(
        self,
        symbol: str,
        market_data: Any,
        fundamentals: Any = None,
        timeframe: str | None = None,
    ) -> dict[str, Any]:

        try:

            indicator_data = self.calculate_indicators(
                market_data
            )

            latest = indicator_data

            if hasattr(
                indicator_data,
                "iloc",
            ):

                if len(indicator_data) == 0:
                    raise ValueError(
                        "Indicator data is empty"
                    )

                latest = indicator_data.iloc[-1]

            # -------------------------------------------------
            # SCORING
            # -------------------------------------------------

            score_result = None

            if self.scoring_engine is not None:

                score_method = getattr(
                    self.scoring_engine,
                    "score",
                    None,
                )

                if callable(score_method):

                    score_result = score_method(
                        latest,
                        self.rules,
                        fundamentals,
                    )

            # -------------------------------------------------
            # SIGNAL
            # -------------------------------------------------

            signal_result = None

            if (
                self.signal_engine is not None
                and score_result is not None
            ):

                generate = getattr(
                    self.signal_engine,
                    "generate",
                    None,
                )

                if callable(generate):

                    signal_result = generate(
                        scoring_result=score_result,
                        market_data=latest,
                        symbol=symbol,
                        timeframe=timeframe,
                    )

            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------

            result: dict[str, Any] = {
                "symbol": symbol,
                "timeframe": timeframe,
                "market_data": market_data,
                "indicators": indicator_data,
                "fundamentals": fundamentals,
                "score": score_result,
                "signal": signal_result,
                "status": "OK",
            }

            return result

        except Exception as exc:

            logger.exception(
                "Failed processing %s",
                symbol,
            )

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "status": "ERROR",
                "error": str(exc),
            }

    # =========================================================
    # NORMALIZE SCANNER OUTPUT
    # =========================================================

    @staticmethod
    def _extract_symbol(
        item: Any,
    ) -> str | None:

        if isinstance(item, Mapping):

            for key in (
                "symbol",
                "tradingsymbol",
                "ticker",
            ):

                if item.get(key):
                    return str(
                        item[key]
                    )

        for key in (
            "symbol",
            "tradingsymbol",
            "ticker",
        ):

            value = getattr(
                item,
                key,
                None,
            )

            if value:
                return str(value)

        if isinstance(item, str):
            return item

        return None

    # =========================================================
    # RANKING
    # =========================================================

    def rank(
        self,
        results: list[Any],
    ) -> Any:

        if self.ranking is None:
            return results

        rank_method = getattr(
            self.ranking,
            "rank",
            None,
        )

        if not callable(rank_method):
            return results

        try:
            return rank_method(
                results
            )
        except Exception:
            logger.exception(
                "Ranking failed"
            )
            return results

    # =========================================================
    # DASHBOARD
    # =========================================================

    def build_summary(
        self,
        ranked: Any,
    ) -> Any:

        if self.dashboard is None:
            return None

        build = getattr(
            self.dashboard,
            "build",
            None,
        )

        if not callable(build):
            return None

        try:
            return build(
                ranked
            )
        except Exception:
            logger.exception(
                "Dashboard summary failed"
            )
            return None

    # =========================================================
    # MASTER RUN
    # =========================================================

    def run(
        self,
        symbols: Iterable[str],
        capital: float | None = None,
        timeframe: str | None = None,
    ) -> tuple[Any, Any]:

        symbols = list(symbols)

        # -----------------------------------------------------
        # Existing scanner compatibility
        # -----------------------------------------------------

        if (
            self.indicator_engine is None
            and self.scoring_engine is None
            and self.signal_engine is None
        ):

            signals = self.scan_symbols(
                symbols,
                capital,
            )

            ranked = self.rank(
                signals
            )

            summary = self.build_summary(
                ranked
            )

            return ranked, summary

        # -----------------------------------------------------
        # Full TrendForge pipeline
        # -----------------------------------------------------

        results: list[dict[str, Any]] = []

        for symbol in symbols:

            try:

                raw_data = self.scan_symbols(
                    [symbol],
                    capital,
                )

                # Scanner may return:
                # list / dict / dataframe / single object

                market_data = raw_data

                if isinstance(
                    raw_data,
                    (list, tuple),
                ):

                    if not raw_data:
                        continue

                    market_data = raw_data[0]

                elif isinstance(
                    raw_data,
                    Mapping,
                ):

                    market_data = raw_data

                result = self.process_stock(
                    symbol=symbol,
                    market_data=market_data,
                    timeframe=timeframe,
                )

                results.append(
                    result
                )

            except Exception as exc:

                logger.exception(
                    "Pipeline failed for %s",
                    symbol,
                )

                results.append(
                    {
                        "symbol": symbol,
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )

        ranked = self.rank(
            results
        )

        summary = self.build_summary(
            ranked
        )

        return ranked, summary

    # =========================================================
    # DIRECT RESULT PROCESSING
    # =========================================================

    def run_data(
        self,
        data: Mapping[str, Any],
        timeframe: str | None = None,
    ) -> dict[str, Any]:

        symbol = str(
            data.get(
                "symbol",
                "",
            )
        )

        market_data = data.get(
            "market_data",
            data.get(
                "data",
                data,
            ),
        )

        fundamentals = data.get(
            "fundamentals"
        )

        return self.process_stock(
            symbol=symbol,
            market_data=market_data,
            fundamentals=fundamentals,
            timeframe=timeframe,
        )

    # =========================================================
    # BATCH DATA
    # =========================================================

    def run_batch(
        self,
        records: Iterable[Mapping[str, Any]],
        timeframe: str | None = None,
    ) -> list[dict[str, Any]]:

        results = []

        for record in records:

            results.append(
                self.run_data(
                    record,
                    timeframe=timeframe,
                )
            )

        return results

    # =========================================================
    # HEALTH
    # =========================================================

    def health(self) -> dict[str, Any]:

        return {
            "status": "healthy",
            "version": self.VERSION,
            "scanner": self.scanner is not None,
            "indicator_engine": (
                self.indicator_engine is not None
            ),
            "rules": self.rules is not None,
            "scoring_engine": (
                self.scoring_engine is not None
            ),
            "signal_engine": (
                self.signal_engine is not None
            ),
            "ranking": self.ranking is not None,
            "dashboard": self.dashboard is not None,
        }


# =============================================================
# FACTORY
# =============================================================

def build_pipeline(
    scanner: Any,
    ranking: Any = None,
    dashboard: Any = None,
    indicator_engine: Any = None,
    rules: Any = None,
    scoring_engine: Any = None,
    signal_engine: Any = None,
) -> ScanPipeline:

    return ScanPipeline(
        scanner=scanner,
        ranking=ranking,
        dashboard=dashboard,
        indicator_engine=indicator_engine,
        rules=rules,
        scoring_engine=scoring_engine,
        signal_engine=signal_engine,
    )