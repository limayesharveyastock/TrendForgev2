"""
TrendForge v2
Screener Provider
"""

from __future__ import annotations

import logging

from api.fundamentals import FundamentalData
from api.providers.base_provider import BaseProvider
from api.providers.http_client import HTTPClient

logger = logging.getLogger(__name__)


class ScreenerProvider(BaseProvider):
    """
    Screener Provider

    This class is responsible for obtaining
    company fundamentals.

    NOTE:
    The actual fetch implementation depends on the
    data source being used.
    """

    BASE_URL = "https://www.screener.in"

    def __init__(self):

        self.http = HTTPClient()

        logger.info(
            "ScreenerProvider initialized."
        )

    # --------------------------------------------------

    def get_fundamentals(
        self,
        symbol: str,
    ) -> FundamentalData:
        """
        Returns company fundamentals.

        Implementation will be added once the
        data source is finalized.
        """

        logger.info(
            "Loading fundamentals for %s",
            symbol,
        )

        return FundamentalData(
            symbol=symbol,
        )

    # --------------------------------------------------

    def search_company(
        self,
        symbol: str,
    ) -> str | None:
        """
        Placeholder for company lookup.
        """

        logger.info(
            "Searching company %s",
            symbol,
        )

        return None

    # --------------------------------------------------

    def health(self):

        return {
            "provider": "Screener",
            "status": "ready",
        }