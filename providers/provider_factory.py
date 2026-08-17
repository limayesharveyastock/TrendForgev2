"""
TrendForge v2
Provider Factory

Centralized construction of the TrendForge provider stack.

This module:
- creates market-data providers
- creates fundamental providers
- creates ProviderManager
- creates MarketDataRouter
- keeps provider construction out of scanner/engine code

No trading logic belongs here.
"""

from __future__ import annotations

import logging
from typing import Any

from providers.market_data_router import (
    MarketDataRouter,
)
from providers.provider_manager import (
    ProviderManager,
)
from providers.screener_provider import (
    ScreenerProvider,
)
from providers.tijori_provider import (
    TijoriProvider,
)

logger = logging.getLogger(__name__)


class ProviderFactory:

    VERSION = "2.1"

    def __init__(
        self,
        kite: Any = None,
        nse: Any = None,
        yfinance: Any = None,
        tijori: Any = None,
        screener: Any = None,
    ) -> None:

        self.kite = kite
        self.nse = nse
        self.yfinance = yfinance

        self.tijori = (
            tijori
            if tijori is not None
            else TijoriProvider()
        )

        self.screener = (
            screener
            if screener is not None
            else ScreenerProvider()
        )

    # =========================================================
    # PROVIDER MANAGER
    # =========================================================

    def create_manager(
        self,
    ) -> ProviderManager:

        return ProviderManager(
            kite=self.kite,
            nse=self.nse,
            yfinance=self.yfinance,
        )

    # =========================================================
    # MARKET DATA ROUTER
    # =========================================================

    def create_market_router(
        self,
        manager: ProviderManager | None = None,
    ) -> MarketDataRouter:

        if manager is None:
            manager = self.create_manager()

        return MarketDataRouter(
            provider_manager=manager,
        )

    # =========================================================
    # FUNDAMENTALS
    # =========================================================

    def create_fundamental_providers(
        self,
    ) -> dict[str, Any]:

        return {
            "tijori": self.tijori,
            "screener": self.screener,
            "yfinance": self.yfinance,
        }

    # =========================================================
    # COMPLETE STACK
    # =========================================================

    def create_stack(
        self,
    ) -> dict[str, Any]:

        manager = self.create_manager()

        market_router = (
            self.create_market_router(
                manager
            )
        )

        return {
            "provider_manager": manager,
            "market_router": market_router,
            "fundamentals": (
                self.create_fundamental_providers()
            ),
        }

    # =========================================================
    # HEALTH
    # =========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        stack = self.create_stack()

        manager = stack[
            "provider_manager"
        ]

        result = {
            "factory": {
                "available": True,
                "version": self.VERSION,
            },
            "market_data": {},
            "fundamentals": {},
        }

        try:

            result[
                "market_data"
            ] = manager.health()

        except Exception as exc:

            result[
                "market_data"
            ] = {
                "healthy": False,
                "error": str(exc),
            }

        for name, provider in (
            stack[
                "fundamentals"
            ].items()
        ):

            if provider is None:

                result[
                    "fundamentals"
                ][name] = {
                    "available": False,
                }

                continue

            method = getattr(
                provider,
                "health",
                None,
            )

            if not callable(method):

                result[
                    "fundamentals"
                ][name] = {
                    "available": True,
                }

                continue

            try:

                result[
                    "fundamentals"
                ][name] = method()

            except Exception as exc:

                result[
                    "fundamentals"
                ][name] = {
                    "available": True,
                    "healthy": False,
                    "error": str(exc),
                }

        return result


# =============================================================
# FACTORY FUNCTION
# =============================================================

def create_provider_stack(
    kite: Any = None,
    nse: Any = None,
    yfinance: Any = None,
    tijori: Any = None,
    screener: Any = None,
) -> dict[str, Any]:

    factory = ProviderFactory(
        kite=kite,
        nse=nse,
        yfinance=yfinance,
        tijori=tijori,
        screener=screener,
    )

    return factory.create_stack()