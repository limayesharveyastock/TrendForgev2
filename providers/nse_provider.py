"""
TrendForge v2
NSE Market Data Provider

Responsibilities
----------------
- NSE market status
- Equity quotes
- Index data
- Option chains
- FII/DII
- Corporate actions
- Bulk deals
- Block deals
- Market breadth
- Gainers / losers
- Holidays
- Circulars
- Session management
- Retry + caching
"""

from __future__ import annotations

import logging
import threading
import time
from functools import wraps
from typing import Any

import requests


logger = logging.getLogger(__name__)


class NSEProvider:

    VERSION = "2.1"

    BASE_URL = "https://www.nseindia.com"

    CACHE_TTL = 60
    RETRIES = 3
    RETRY_DELAY = 1.0

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0 Safari/537.36"
        ),
        "Accept": (
            "application/json,"
            "text/plain,"
            "*/*"
        ),
        "Accept-Language": (
            "en-US,en;q=0.9"
        ),
        "Referer": (
            "https://www.nseindia.com/"
        ),
        "Connection": "keep-alive",
    }

    _instance = None
    _lock = threading.Lock()

    # =========================================================
    # SINGLETON
    # =========================================================

    def __new__(cls):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:

                    cls._instance = (
                        super().__new__(cls)
                    )

        return cls._instance

    def __init__(self):

        if getattr(
            self,
            "_initialized",
            False,
        ):
            return

        self.session = requests.Session()

        self.session.headers.update(
            self.HEADERS
        )

        self.cache: dict[
            str,
            tuple[Any, float],
        ] = {}

        self._initialized = True

        self._initialize_session()

    # =========================================================
    # SESSION
    # =========================================================

    def _initialize_session(self) -> None:

        try:

            response = self.session.get(
                self.BASE_URL,
                timeout=10,
            )

            response.raise_for_status()

            logger.info(
                "NSE session initialized"
            )

        except Exception as exc:

            logger.warning(
                "NSE session initialization failed: %s",
                exc,
            )

    def refresh_session(self) -> None:

        try:

            self.session.close()

        except Exception:
            pass

        self.session = requests.Session()

        self.session.headers.update(
            self.HEADERS
        )

        self._initialize_session()

    # =========================================================
    # CACHE
    # =========================================================

    def _cache_get(
        self,
        key: str,
    ) -> Any:

        item = self.cache.get(
            key
        )

        if item is None:
            return None

        value, timestamp = item

        if (
            time.time()
            - timestamp
            > self.CACHE_TTL
        ):

            self.cache.pop(
                key,
                None,
            )

            return None

        return value

    def _cache_set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.cache[key] = (
            value,
            time.time(),
        )

    def clear_cache(self) -> None:

        self.cache.clear()

    # =========================================================
    # HTTP
    # =========================================================

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        cache: bool = True,
    ) -> Any:

        params = params or {}

        cache_key = (
            endpoint
            + "?"
            + "&".join(
                f"{key}={value}"
                for key, value in sorted(
                    params.items()
                )
            )
        )

        if cache:

            cached = self._cache_get(
                cache_key
            )

            if cached is not None:
                return cached

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        last_error = None

        for attempt in range(
            self.RETRIES
        ):

            try:

                response = (
                    self.session.get(
                        url,
                        params=params,
                        timeout=15,
                    )
                )

                # NSE may return 401/403 when
                # the session expires.

                if response.status_code in (
                    401,
                    403,
                ):

                    self.refresh_session()

                    continue

                response.raise_for_status()

                data = response.json()

                if cache:

                    self._cache_set(
                        cache_key,
                        data,
                    )

                return data

            except Exception as exc:

                last_error = exc

                logger.warning(
                    "NSE request failed "
                    "(attempt %s/%s): %s",
                    attempt + 1,
                    self.RETRIES,
                    exc,
                )

                if (
                    attempt
                    < self.RETRIES - 1
                ):

                    time.sleep(
                        self.RETRY_DELAY
                        * (2 ** attempt)
                    )

        raise RuntimeError(
            f"NSE request failed: "
            f"{last_error}"
        )

    # =========================================================
    # MARKET STATUS
    # =========================================================

    def market_status(self):

        return self._get(
            "/api/marketStatus"
        )

    # =========================================================
    # EQUITY QUOTE
    # =========================================================

    def equity_quote(
        self,
        symbol: str,
    ):

        return self._get(
            "/api/quote-equity",
            params={
                "symbol": symbol.upper()
            },
        )

    def quote(
        self,
        symbol: str,
    ):

        return self.equity_quote(
            symbol
        )

    # =========================================================
    # INDEX QUOTE
    # =========================================================

    def index_quote(
        self,
        index_name: str,
    ):

        return self._get(
            "/api/allIndices",
            params={
                "index": index_name
            },
        )

    # =========================================================
    # MAJOR INDICES
    # =========================================================

    def nifty50(self):

        return self.index_quote(
            "NIFTY 50"
        )

    def banknifty(self):

        return self.index_quote(
            "NIFTY BANK"
        )

    def finnifty(self):

        return self.index_quote(
            "NIFTY FINANCIAL SERVICES"
        )

    def midcap(self):

        return self.index_quote(
            "NIFTY MIDCAP 100"
        )

    def smallcap(self):

        return self.index_quote(
            "NIFTY SMALLCAP 100"
        )

    # =========================================================
    # OPTION CHAIN
    # =========================================================

    def option_chain(
        self,
        symbol: str,
    ):

        return self._get(
            "/api/option-chain-equities",
            params={
                "symbol": symbol.upper()
            },
            cache=False,
        )

    def index_option_chain(
        self,
        symbol: str,
    ):

        return self._get(
            "/api/option-chain-indices",
            params={
                "symbol": symbol.upper()
            },
            cache=False,
        )

    # =========================================================
    # MARKET BREADTH
    # =========================================================

    def market_breadth(
        self,
    ):

        return self._get(
            "/api/equity-stockIndices",
            params={
                "index": "NIFTY 500"
            },
        )

    def advance_decline(
        self,
    ) -> dict[str, int]:

        data = self.market_breadth()

        advances = 0
        declines = 0
        unchanged = 0

        rows = []

        if isinstance(
            data,
            dict,
        ):

            rows = data.get(
                "data",
                [],
            )

        for stock in rows:

            change = stock.get(
                "change",
                0,
            )

            try:
                change = float(
                    change
                )
            except (
                TypeError,
                ValueError,
            ):
                change = 0

            if change > 0:

                advances += 1

            elif change < 0:

                declines += 1

            else:

                unchanged += 1

        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
        }

    # =========================================================
    # GAINERS
    # =========================================================

    def top_gainers(self):

        return self._get(
            "/api/live-analysis-variations",
            params={
                "index": "gainers"
            },
        )

    # =========================================================
    # LOSERS
    # =========================================================

    def top_losers(self):

        return self._get(
            "/api/live-analysis-variations",
            params={
                "index": "losers"
            },
        )

    # =========================================================
    # MOST ACTIVE
    # =========================================================

    def most_active(self):

        return self._get(
            "/api/live-analysis-most-active-securities"
        )

    # =========================================================
    # FII / DII
    # =========================================================

    def fii_dii(self):

        return self._get(
            "/api/fiiDiiTradeReact",
            cache=False,
        )

    # =========================================================
    # CORPORATE ACTIONS
    # =========================================================

    def corporate_actions(
        self,
    ):

        return self._get(
            "/api/corporates-corporateActions",
            cache=False,
        )

    # =========================================================
    # BULK DEALS
    # =========================================================

    def bulk_deals(
        self,
    ):

        return self._get(
            "/api/historicalOR/bulk-deals",
            cache=False,
        )

    # =========================================================
    # BLOCK DEALS
    # =========================================================

    def block_deals(
        self,
    ):

        return self._get(
            "/api/historicalOR/block-deals",
            cache=False,
        )

    # =========================================================
    # HOLIDAYS
    # =========================================================

    def holidays(
        self,
    ):

        return self._get(
            "/api/holiday-master",
            params={
                "type": "trading"
            },
            cache=False,
        )

    # =========================================================
    # CIRCULARS
    # =========================================================

    def circulars(
        self,
    ):

        return self._get(
            "/api/circulars",
            cache=False,
        )

    # =========================================================
    # BHAVCOPY / REPORTS
    # =========================================================

    def reports(
        self,
    ):

        return self._get(
            "/api/reports",
            params={
                "archives": "downloads"
            },
            cache=False,
        )

    # =========================================================
    # CONVENIENCE
    # =========================================================

    def stock_snapshot(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        quote = self.equity_quote(
            symbol
        )

        return {
            "symbol": symbol.upper(),
            "quote": quote,
        }

    # =========================================================
    # HEALTH
    # =========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return {
            "provider": "nse",
            "version": self.VERSION,
            "session": (
                self.session is not None
            ),
            "base_url": self.BASE_URL,
        }

    def ping(
        self,
    ) -> bool:

        try:

            self.market_status()

            return True

        except Exception:

            logger.exception(
                "NSE ping failed"
            )

            return False


# =============================================================
# SINGLETON
# =============================================================

nse_provider = NSEProvider()


# =============================================================
# FACTORY
# =============================================================

def get_nse_provider() -> NSEProvider:

    return nse_provider