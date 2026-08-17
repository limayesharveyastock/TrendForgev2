"""
TrendForge v2
Market Data Router

Purpose
-------
Provides a stable interface between scanner/engines and the
underlying market-data providers.

Provider selection:
    Historical OHLCV -> ProviderManager
    Live Price       -> ProviderManager
    Options          -> ProviderManager
    Corporate Events -> ProviderManager

The router contains no trading logic.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MarketDataRouter:

    VERSION = "2.1"

    def __init__(
        self,
        provider_manager: Any,
    ) -> None:

        if provider_manager is None:
            raise ValueError(
                "provider_manager is required"
            )

        self.providers = provider_manager

    # =========================================================
    # HISTORICAL OHLCV
    # =========================================================

    def historical(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> Any:

        return self.providers.historical_data(
            symbol=symbol,
            period=period,
            interval=interval,
        )

    # =========================================================
    # LIVE PRICE
    # =========================================================

    def price(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        return self.providers.live_price(
            symbol
        )

    # =========================================================
    # FUNDAMENTALS
    # =========================================================

    def fundamentals(
        self,
        symbol: str,
    ) -> Any:

        return self.providers.fundamentals(
            symbol
        )

    # =========================================================
    # NEWS
    # =========================================================

    def news(
        self,
        symbol: str,
    ) -> Any:

        return self.providers.news(
            symbol
        )

    # =========================================================
    # CORPORATE ACTIONS
    # =========================================================

    def corporate_actions(
        self,
    ) -> Any:

        return self.providers.corporate_actions()

    # =========================================================
    # BULK DEALS
    # =========================================================

    def bulk_deals(
        self,
    ) -> Any:

        return self.providers.bulk_deals()

    # =========================================================
    # BLOCK DEALS
    # =========================================================

    def block_deals(
        self,
    ) -> Any:

        return self.providers.block_deals()

    # =========================================================
    # MARKET BREADTH
    # =========================================================

    def market_breadth(
        self,
    ) -> Any:

        method = getattr(
            self.providers,
            "market_breadth",
            None,
        )

        if not callable(method):
            return {}

        return method()

    # =========================================================
    # OPTIONS
    # =========================================================

    def option_chain(
        self,
        symbol: str,
        index: bool = False,
    ) -> Any:

        return self.providers.option_chain(
            symbol=symbol,
            index=index,
        )

    # =========================================================
    # SAFE SNAPSHOT
    # =========================================================

    def snapshot(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> dict[str, Any]:

        result: dict[str, Any] = {
            "symbol": symbol.upper(),
            "version": self.VERSION,
            "historical": None,
            "price": None,
            "fundamentals": None,
            "news": [],
            "errors": [],
        }

        # -----------------------------------------------------
        # HISTORICAL
        # -----------------------------------------------------

        try:

            result["historical"] = (
                self.historical(
                    symbol=symbol,
                    period=period,
                    interval=interval,
                )
            )

        except Exception as exc:

            result["errors"].append(
                {
                    "component": "historical",
                    "error": str(exc),
                }
            )

            logger.warning(
                "Historical snapshot failed for %s: %s",
                symbol,
                exc,
            )

        # -----------------------------------------------------
        # PRICE
        # -----------------------------------------------------

        try:

            result["price"] = self.price(
                symbol
            )

        except Exception as exc:

            result["errors"].append(
                {
                    "component": "price",
                    "error": str(exc),
                }
            )

            logger.warning(
                "Price snapshot failed for %s: %s",
                symbol,
                exc,
            )

        # -----------------------------------------------------
        # FUNDAMENTALS
        # -----------------------------------------------------

        try:

            result["fundamentals"] = (
                self.fundamentals(
                    symbol
                )
            )

        except Exception as exc:

            result["errors"].append(
                {
                    "component": "fundamentals",
                    "error": str(exc),
                }
            )

            logger.warning(
                "Fundamental snapshot failed "
                "for %s: %s",
                symbol,
                exc,
            )

        # -----------------------------------------------------
        # NEWS
        # -----------------------------------------------------

        try:

            result["news"] = (
                self.news(
                    symbol
                )
                or []
            )

        except Exception as exc:

            result["errors"].append(
                {
                    "component": "news",
                    "error": str(exc),
                }
            )

        return result

    # =========================================================
    # HEALTH
    # =========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        provider_health = {}

        method = getattr(
            self.providers,
            "health",
            None,
        )

        if callable(method):

            try:
                provider_health = method()

            except Exception as exc:

                provider_health = {
                    "healthy": False,
                    "error": str(exc),
                }

        return {
            "router": {
                "available": True,
                "version": self.VERSION,
            },
            "providers": provider_health,
        }

    # =========================================================
    # PING
    # =========================================================

    def ping(
        self,
    ) -> dict[str, Any]:

        method = getattr(
            self.providers,
            "ping",
            None,
        )

        if not callable(method):

            return {
                "available": False
            }

        try:

            return method()

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }


# =============================================================
# FACTORY
# =============================================================

def create_market_data_router(
    provider_manager: Any,
) -> MarketDataRouter:

    return MarketDataRouter(
        provider_manager
    )