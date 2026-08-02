"""
providers/nse_provider.py
=========================

Centralized NSE data provider used across TrendForge.

Features
--------
- Index quotes
- Market status
- Option Chain
- Bhavcopy
- Holidays
- Corporate actions
- Circulars
- Bulk / Block Deals
- FII/DII data
- Market Breadth
- Gainers / Losers
- Most Active Stocks
- Retry handling
- In-memory caching
"""

from __future__ import annotations

import logging
import threading
import time
from functools import wraps
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class NSEProvider:
    _instance = None
    _lock = threading.Lock()

    BASE_URL = "https://www.nseindia.com"

    HEADERS = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language":
            "en-US,en;q=0.9",
        "Accept":
            "application/json,text/plain,*/*",
        "Referer":
            "https://www.nseindia.com/",
        "Connection":
            "keep-alive"
    }

    CACHE_TTL = 60

    def __new__(cls):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if hasattr(self, "_initialized"):
            return

        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

        self.cache = {}

        self._initialize_session()

        self._initialized = True

    ####################################################################
    # Session
    ####################################################################

    def _initialize_session(self):

        try:

            self.session.get(
                self.BASE_URL,
                timeout=10
            )

            logger.info("NSE session initialized.")

        except Exception as e:

            logger.exception(e)

    ####################################################################
    # Retry
    ####################################################################

    @staticmethod
    def retry(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            retries = 3
            delay = 1

            for attempt in range(retries):

                try:
                    return func(*args, **kwargs)

                except Exception as e:

                    logger.warning(
                        "Retry %s : %s",
                        attempt + 1,
                        e
                    )

                    time.sleep(delay)

                    delay *= 2

            raise Exception("NSE request failed.")

        return wrapper

    ####################################################################
    # Cache
    ####################################################################

    def _cache_get(self, key):

        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]

        if time.time() - timestamp > self.CACHE_TTL:
            del self.cache[key]
            return None

        return value

    def _cache_set(self, key, value):

        self.cache[key] = (
            value,
            time.time()
        )

    ####################################################################
    # Request
    ####################################################################

    @retry
    def _get(self, endpoint):

        cached = self._cache_get(endpoint)

        if cached is not None:
            return cached

        url = f"{self.BASE_URL}{endpoint}"

        response = self.session.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        self._cache_set(endpoint, data)

        return data

    ####################################################################
    # Market Status
    ####################################################################

    def market_status(self):

        return self._get("/api/marketStatus")

    ####################################################################
    # Index Quote
    ####################################################################

    def index_quote(self, index_name):

        endpoint = (
            f"/api/allIndices?index={index_name}"
        )

        return self._get(endpoint)

    ####################################################################
    # Equity Quote
    ####################################################################

    def equity_quote(self, symbol):

        endpoint = (
            f"/api/quote-equity?symbol={symbol}"
        )

        return self._get(endpoint)

    ####################################################################
    # Option Chain
    ####################################################################

    def option_chain(self, symbol):

        endpoint = (
            f"/api/option-chain-equities?symbol={symbol}"
        )

        return self._get(endpoint)

    ####################################################################
    # Market Breadth
    ####################################################################

    def market_breadth(self):

        return self._get("/api/equity-stockIndices?index=NIFTY%2050")

    ####################################################################
    # Top Gainers
    ####################################################################

    def top_gainers(self):

        return self._get(
            "/api/live-analysis-variations?index=gainers"
        )

    ####################################################################
    # Top Losers
    ####################################################################

    def top_losers(self):

        return self._get(
            "/api/live-analysis-variations?index=losers"
        )

    ####################################################################
    # Most Active
    ####################################################################

    def most_active(self):

        return self._get(
            "/api/live-analysis-most-active-securities"
        )

    ####################################################################
    # FII DII
    ####################################################################

    def fii_dii(self):

        return self._get(
            "/api/fiiDiiTradeReact"
        )

    ####################################################################
    # Holidays
    ####################################################################

    def holidays(self):

        return self._get(
            "/api/holiday-master?type=trading"
        )

    ####################################################################
    # Circulars
    ####################################################################

    def circulars(self):

        return self._get(
            "/api/circulars"
        )

    ####################################################################
    # Corporate Actions
    ####################################################################

    def corporate_actions(self):

        return self._get(
            "/api/corporates-corporateActions"
        )

    ####################################################################
    # Bulk Deals
    ####################################################################

    def bulk_deals(self):

        return self._get(
            "/api/historicalOR/bulk-deals"
        )

    ####################################################################
    # Block Deals
    ####################################################################

    def block_deals(self):

        return self._get(
            "/api/historicalOR/block-deals"
        )

    ####################################################################
    # Bhavcopy
    ####################################################################

    def bhavcopy(self):

        return self._get(
            "/api/reports?archives=downloads"
        )

    ####################################################################
    # Advance Decline
    ####################################################################

    def advance_decline(self):

        data = self.market_breadth()

        advances = 0
        declines = 0
        unchanged = 0

        try:

            for stock in data["data"]:

                change = stock.get("change", 0)

                if change > 0:
                    advances += 1
                elif change < 0:
                    declines += 1
                else:
                    unchanged += 1

        except Exception:
            pass

        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged
        }

    ####################################################################
    # Convenience
    ####################################################################

    def nifty50(self):

        return self.index_quote("NIFTY 50")

    def banknifty(self):

        return self.index_quote("NIFTY BANK")

    def finnifty(self):

        return self.index_quote("NIFTY FINANCIAL SERVICES")

    def midcap(self):

        return self.index_quote("NIFTY MIDCAP 100")

    def smallcap(self):

        return self.index_quote("NIFTY SMALLCAP 100")


nse_provider = NSEProvider()

class NSEProvider:

    BASE = "https://www.nseindia.com/api"

    def __init__(self):

        self.session = requests.Session()

    def market_status(self):

        return self.session.get(

            f"{self.BASE}/marketStatus"

        ).json()

    def quote(self, symbol):

        return self.session.get(

            f"{self.BASE}/quote-equity",

            params={

                "symbol": symbol

            }

        ).json()