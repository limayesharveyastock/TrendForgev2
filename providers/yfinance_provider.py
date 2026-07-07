"""
providers/yfinance_provider.py
================================

Yahoo Finance provider for TrendForge.

Purpose
-------
Provides market data when:
- Kite is unavailable
- NSE endpoints fail
- Historical data beyond broker limits is needed
- Global indices are required

Features
--------
✓ Historical OHLCV
✓ Live quote
✓ Company info
✓ Financials
✓ Balance Sheet
✓ Cash Flow
✓ Earnings
✓ Dividends
✓ Splits
✓ Recommendations
✓ Option Chain
✓ Multiple ticker download
✓ Retry
✓ In-memory cache
✓ Thread-safe singleton
"""

from __future__ import annotations

import logging
import threading
import time
from functools import wraps
from typing import Dict, List, Optional, Any

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class YahooFinanceProvider:

    _instance = None
    _lock = threading.Lock()

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

        self.cache = {}

        self._initialized = True

    ####################################################################
    # Cache
    ####################################################################

    def _cache_get(self, key):

        if key not in self.cache:
            return None

        value, ts = self.cache[key]

        if time.time() - ts > self.CACHE_TTL:
            del self.cache[key]
            return None

        return value

    def _cache_set(self, key, value):

        self.cache[key] = (
            value,
            time.time()
        )

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
                        "%s failed (%s/3): %s",
                        func.__name__,
                        attempt + 1,
                        e
                    )

                    time.sleep(delay)

                    delay *= 2

            raise Exception(
                f"{func.__name__} failed after retries."
            )

        return wrapper

    ####################################################################
    # Internal
    ####################################################################

    def ticker(self, symbol: str):

        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol = f"{symbol}.NS"

        return yf.Ticker(symbol)

    ####################################################################
    # Historical Data
    ####################################################################

    @retry
    def historical_data(
            self,
            symbol: str,
            period="1y",
            interval="1d",
            auto_adjust=True
    ) -> pd.DataFrame:

        key = (
            "history",
            symbol,
            period,
            interval
        )

        cached = self._cache_get(key)

        if cached is not None:
            return cached

        df = self.ticker(symbol).history(
            period=period,
            interval=interval,
            auto_adjust=auto_adjust
        )

        self._cache_set(key, df)

        return df

    ####################################################################
    # Download Multiple
    ####################################################################

    @retry
    def download(
            self,
            symbols: List[str],
            period="6mo",
            interval="1d"
    ) -> pd.DataFrame:

        symbols = [
            s if s.endswith(".NS") else s + ".NS"
            for s in symbols
        ]

        return yf.download(
            symbols,
            period=period,
            interval=interval,
            group_by="ticker",
            threads=True,
            progress=False
        )

    ####################################################################
    # Live Quote
    ####################################################################

    @retry
    def live_price(self, symbol):

        data = self.ticker(symbol).fast_info

        return {
            "symbol": symbol,
            "last_price": data.get("lastPrice"),
            "open": data.get("open"),
            "high": data.get("dayHigh"),
            "low": data.get("dayLow"),
            "volume": data.get("lastVolume")
        }

    ####################################################################
    # Company Information
    ####################################################################

    @retry
    def company_info(self, symbol):

        return self.ticker(symbol).info

    ####################################################################
    # Financial Statements
    ####################################################################

    @retry
    def financials(self, symbol):

        return self.ticker(symbol).financials

    @retry
    def quarterly_financials(self, symbol):

        return self.ticker(symbol).quarterly_financials

    ####################################################################
    # Balance Sheet
    ####################################################################

    @retry
    def balance_sheet(self, symbol):

        return self.ticker(symbol).balance_sheet

    @retry
    def quarterly_balance_sheet(self, symbol):

        return self.ticker(symbol).quarterly_balance_sheet

    ####################################################################
    # Cash Flow
    ####################################################################

    @retry
    def cashflow(self, symbol):

        return self.ticker(symbol).cashflow

    @retry
    def quarterly_cashflow(self, symbol):

        return self.ticker(symbol).quarterly_cashflow

    ####################################################################
    # Earnings
    ####################################################################

    @retry
    def earnings(self, symbol):

        return self.ticker(symbol).earnings

    @retry
    def quarterly_earnings(self, symbol):

        return self.ticker(symbol).quarterly_earnings

    ####################################################################
    # Dividends
    ####################################################################

    @retry
    def dividends(self, symbol):

        return self.ticker(symbol).dividends

    ####################################################################
    # Splits
    ####################################################################

    @retry
    def splits(self, symbol):

        return self.ticker(symbol).splits

    ####################################################################
    # Insider Transactions
    ####################################################################

    @retry
    def insider_transactions(self, symbol):

        return self.ticker(symbol).insider_transactions

    ####################################################################
    # Recommendations
    ####################################################################

    @retry
    def recommendations(self, symbol):

        return self.ticker(symbol).recommendations

    ####################################################################
    # Sustainability
    ####################################################################

    @retry
    def sustainability(self, symbol):

        return self.ticker(symbol).sustainability

    ####################################################################
    # Option Chain
    ####################################################################

    @retry
    def option_expiries(self, symbol):

        return self.ticker(symbol).options

    @retry
    def option_chain(
            self,
            symbol,
            expiry
    ):

        return self.ticker(symbol).option_chain(expiry)

    ####################################################################
    # News
    ####################################################################

    @retry
    def news(self, symbol):

        try:
            return self.ticker(symbol).news
        except Exception:
            return []

    ####################################################################
    # Major Holders
    ####################################################################

    @retry
    def major_holders(self, symbol):

        return self.ticker(symbol).major_holders

    ####################################################################
    # Institutional Holders
    ####################################################################

    @retry
    def institutional_holders(self, symbol):

        return self.ticker(symbol).institutional_holders

    ####################################################################
    # Mutual Fund Holders
    ####################################################################

    @retry
    def mutualfund_holders(self, symbol):

        return self.ticker(symbol).mutualfund_holders

    ####################################################################
    # Convenience
    ####################################################################

    def nifty50(self):

        return self.historical_data("^NSEI")

    def banknifty(self):

        return self.historical_data("^NSEBANK")

    def sensex(self):

        return self.historical_data("^BSESN")

    def india_vix(self):

        return self.historical_data("^INDIAVIX")

    ####################################################################
    # Health Check
    ####################################################################

    def ping(self):

        try:

            self.live_price("RELIANCE")

            return True

        except Exception:

            return False


# Singleton instance
yfinance_provider = YahooFinanceProvider()