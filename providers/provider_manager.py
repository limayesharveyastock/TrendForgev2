"""
TrendForge v2
Unified Provider Manager

Provider priority:
    Kite -> NSE -> YFinance

Purpose:
    Provide one interface to the scanner while allowing
    automatic fallback between market-data providers.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ProviderManager:
    VERSION = "2.1"

    def __init__(
        self,
        kite: Any = None,
        nse: Any = None,
        yfinance: Any = None,
    ) -> None:
        self.kite = kite
        self.nse = nse
        self.yfinance = yfinance

    # =========================================================
    # GENERIC SAFE CALL
    # =========================================================

    @staticmethod
    def _call(
        provider: Any,
        method: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        if provider is None:
            raise RuntimeError("Provider unavailable")

        function = getattr(
            provider,
            method,
            None,
        )

        if not callable(function):
            raise AttributeError(
                f"{type(provider).__name__} "
                f"does not implement {method}()"
            )

        return function(
            *args,
            **kwargs,
        )

    # =========================================================
    # HISTORICAL DATA
    # =========================================================

    def historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ):

        errors: list[str] = []

        # Kite requires an instrument token.
        if (
            self.kite is not None
            and str(symbol).isdigit()
        ):
            try:
                return self._call(
                    self.kite,
                    "candles",
                    instrument_token=int(symbol),
                    days=self._period_days(period),
                    interval=self._kite_interval(interval),
                )
            except Exception as exc:
                errors.append(f"kite: {exc}")

        # YFinance handles symbols directly.
        if self.yfinance is not None:
            try:
                return self._call(
                    self.yfinance,
                    "historical_data",
                    symbol=symbol,
                    period=period,
                    interval=interval,
                )
            except Exception as exc:
                errors.append(f"yfinance: {exc}")

        raise RuntimeError(
            "No historical-data provider succeeded"
            + (
                f": {' | '.join(errors)}"
                if errors
                else ""
            )
        )

    # =========================================================
    # LIVE PRICE
    # =========================================================

    def live_price(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        errors: list[str] = []

        # 1. Kite
        if self.kite is not None:
            try:
                data = self._call(
                    self.kite,
                    "ltp",
                    symbol,
                )

                if data:
                    return {
                        "provider": "kite",
                        "symbol": symbol.upper(),
                        "data": data,
                    }

            except Exception as exc:
                errors.append(f"kite: {exc}")

        # 2. NSE
        if self.nse is not None:
            try:
                data = self._call(
                    self.nse,
                    "quote",
                    symbol,
                )

                if data:
                    return {
                        "provider": "nse",
                        "symbol": symbol.upper(),
                        "data": data,
                    }

            except Exception as exc:
                errors.append(f"nse: {exc}")

        # 3. YFinance
        if self.yfinance is not None:
            try:
                data = self._call(
                    self.yfinance,
                    "live_price",
                    symbol,
                )

                if data:
                    return {
                        "provider": "yfinance",
                        "symbol": symbol.upper(),
                        "data": data,
                    }

            except Exception as exc:
                errors.append(f"yfinance: {exc}")

        raise RuntimeError(
            "No live-price provider succeeded"
            + (
                f": {' | '.join(errors)}"
                if errors
                else ""
            )
        )

    # =========================================================
    # FUNDAMENTALS
    # =========================================================

    def fundamentals(
        self,
        symbol: str,
    ) -> Any:

        errors: list[str] = []

        if self.yfinance is not None:
            try:
                return self._call(
                    self.yfinance,
                    "company_info",
                    symbol,
                )
            except Exception as exc:
                errors.append(
                    f"yfinance: {exc}"
                )

        if errors:
            logger.warning(
                "Fundamental providers failed: %s",
                " | ".join(errors),
            )

        return None

    # =========================================================
    # NEWS
    # =========================================================

    def news(
        self,
        symbol: str,
    ) -> list[Any]:

        if self.yfinance is None:
            return []

        try:
            data = self._call(
                self.yfinance,
                "news",
                symbol,
            )

            return data or []

        except Exception as exc:
            logger.warning(
                "News provider failed for %s: %s",
                symbol,
                exc,
            )
            return []

    # =========================================================
    # CORPORATE ACTIONS
    # =========================================================

    def corporate_actions(self):

        if self.nse is None:
            return []

        return self._call(
            self.nse,
            "corporate_actions",
        )

    # =========================================================
    # BULK DEALS
    # =========================================================

    def bulk_deals(self):

        if self.nse is None:
            return []

        return self._call(
            self.nse,
            "bulk_deals",
        )

    # =========================================================
    # BLOCK DEALS
    # =========================================================

    def block_deals(self):

        if self.nse is None:
            return []

        return self._call(
            self.nse,
            "block_deals",
        )

    # =========================================================
    # MARKET BREADTH
    # =========================================================

    def market_breadth(self):

        if self.nse is None:
            return {}

        return self._call(
            self.nse,
            "market_breadth",
        )

    # =========================================================
    # OPTION CHAIN
    # =========================================================

    def option_chain(
        self,
        symbol: str,
        index: bool = False,
    ):

        if self.nse is not None:

            method = (
                "index_option_chain"
                if index
                else "option_chain"
            )

            try:
                return self._call(
                    self.nse,
                    method,
                    symbol,
                )
            except Exception as exc:
                logger.warning(
                    "NSE option chain failed: %s",
                    exc,
                )

        if self.yfinance is not None:

            try:
                expiries = self._call(
                    self.yfinance,
                    "option_expiries",
                    symbol,
                )

                if not expiries:
                    return None

                return self._call(
                    self.yfinance,
                    "option_chain",
                    symbol,
                    expiries[0],
                )

            except Exception as exc:
                logger.warning(
                    "YFinance option chain failed: %s",
                    exc,
                )

        return None

    # =========================================================
    # PROVIDER HEALTH
    # =========================================================

    def health(self) -> dict[str, Any]:

        result: dict[str, Any] = {
            "version": self.VERSION,
            "providers": {},
        }

        for name, provider in (
            ("kite", self.kite),
            ("nse", self.nse),
            ("yfinance", self.yfinance),
        ):

            if provider is None:
                result["providers"][name] = {
                    "available": False,
                }
                continue

            health_method = getattr(
                provider,
                "health",
                None,
            )

            if not callable(health_method):
                result["providers"][name] = {
                    "available": True,
                }
                continue

            try:
                result["providers"][name] = (
                    health_method()
                )
            except Exception as exc:
                result["providers"][name] = {
                    "available": True,
                    "healthy": False,
                    "error": str(exc),
                }

        return result

    # =========================================================
    # PING
    # =========================================================

    def ping(self) -> dict[str, bool]:

        result = {}

        for name, provider in (
            ("kite", self.kite),
            ("nse", self.nse),
            ("yfinance", self.yfinance),
        ):

            if provider is None:
                result[name] = False
                continue

            method = getattr(
                provider,
                "ping",
                None,
            )

            if not callable(method):
                result[name] = False
                continue

            try:
                result[name] = bool(
                    method()
                )
            except Exception:
                result[name] = False

        return result

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _period_days(
        period: str,
    ) -> int:

        return {
            "1d": 2,
            "5d": 7,
            "1mo": 31,
            "3mo": 100,
            "6mo": 190,
            "1y": 370,
            "2y": 740,
            "5y": 1850,
        }.get(
            period,
            370,
        )

    @staticmethod
    def _kite_interval(
        interval: str,
    ) -> str:

        return {
            "1m": "minute",
            "3m": "3minute",
            "5m": "5minute",
            "10m": "10minute",
            "15m": "15minute",
            "30m": "30minute",
            "60m": "60minute",
            "1h": "60minute",
            "1d": "day",
        }.get(
            interval,
            "day",
        )


# =============================================================
# FACTORY
# =============================================================

def create_provider_manager(
    kite: Any = None,
    nse: Any = None,
    yfinance: Any = None,
) -> ProviderManager:

    return ProviderManager(
        kite=kite,
        nse=nse,
        yfinance=yfinance,
    )