"""
TrendForge v2
Yahoo Finance Provider

Fallback market-data provider.

Used for:
- Historical OHLCV
- Intraday data
- Live prices
- Index data
- Fundamental data
- Options
- Institutional ownership
- Mutual-fund ownership
- News
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Iterable

import pandas as pd
import yfinance as yf


logger = logging.getLogger(__name__)


class YahooFinanceProvider:

    VERSION = "2.1"

    CACHE_TTL = 60
    RETRIES = 3
    RETRY_DELAY = 1.0

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

        self.cache: dict[
            Any,
            tuple[Any, float],
        ] = {}

        self._initialized = True

    # =========================================================
    # CACHE
    # =========================================================

    def _cache_get(
        self,
        key: Any,
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
        key: Any,
        value: Any,
    ) -> None:

        self.cache[key] = (
            value,
            time.time(),
        )

    def clear_cache(self) -> None:

        self.cache.clear()

    # =========================================================
    # RETRY
    # =========================================================

    def _execute(
        self,
        method,
        *args,
        **kwargs,
    ):

        last_error = None

        for attempt in range(
            self.RETRIES
        ):

            try:

                return method(
                    *args,
                    **kwargs,
                )

            except Exception as exc:

                last_error = exc

                logger.warning(
                    "YFinance request failed "
                    "(%s/%s): %s",
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
            f"YFinance request failed: "
            f"{last_error}"
        )

    # =========================================================
    # SYMBOL NORMALIZATION
    # =========================================================

    @staticmethod
    def normalize_symbol(
        symbol: str,
    ) -> str:

        symbol = str(
            symbol
        ).strip().upper()

        if (
            symbol.endswith(".NS")
            or symbol.endswith(".BO")
            or symbol.startswith("^")
        ):
            return symbol

        return (
            f"{symbol}.NS"
        )

    def ticker(
        self,
        symbol: str,
    ):

        return yf.Ticker(
            self.normalize_symbol(
                symbol
            )
        )

    # =========================================================
    # HISTORICAL DATA
    # =========================================================

    def historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        auto_adjust: bool = False,
    ) -> pd.DataFrame:

        key = (
            "history",
            symbol,
            period,
            interval,
            auto_adjust,
        )

        cached = self._cache_get(
            key
        )

        if cached is not None:
            return cached

        ticker = self.ticker(
            symbol
        )

        df = self._execute(
            ticker.history,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
        )

        df = self.normalize_ohlcv(
            df
        )

        self._cache_set(
            key,
            df
        )

        return df

    # =========================================================
    # CANDLES
    # =========================================================

    def candles(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> pd.DataFrame:

        return self.historical_data(
            symbol=symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
        )

    # =========================================================
    # OHLCV NORMALIZATION
    # =========================================================

    @staticmethod
    def normalize_ohlcv(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        if df is None:
            return pd.DataFrame()

        if df.empty:
            return df

        result = df.copy()

        # Flatten MultiIndex columns.

        if isinstance(
            result.columns,
            pd.MultiIndex,
        ):

            result.columns = [
                str(column[0])
                for column in result.columns
            ]

        rename_map = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }

        result.rename(
            columns=rename_map,
            inplace=True,
        )

        if (
            isinstance(
                result.index,
                pd.DatetimeIndex,
            )
        ):

            result = result.reset_index()

            if "Datetime" in result.columns:

                result.rename(
                    columns={
                        "Datetime": "date"
                    },
                    inplace=True,
                )

            elif "Date" in result.columns:

                result.rename(
                    columns={
                        "Date": "date"
                    },
                    inplace=True,
                )

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
        ]

        for column in numeric_columns:

            if column in result.columns:

                result[column] = pd.to_numeric(
                    result[column],
                    errors="coerce",
                )

        if "date" in result.columns:

            result["date"] = pd.to_datetime(
                result["date"],
                errors="coerce",
            )

            result.sort_values(
                "date",
                inplace=True,
            )

        result.reset_index(
            drop=True,
            inplace=True,
        )

        return result

    # =========================================================
    # DOWNLOAD MULTIPLE
    # =========================================================

    def download(
        self,
        symbols: Iterable[str],
        period: str = "6mo",
        interval: str = "1d",
    ) -> pd.DataFrame:

        normalized = [
            self.normalize_symbol(
                symbol
            )
            for symbol in symbols
        ]

        return self._execute(
            yf.download,
            normalized,
            period=period,
            interval=interval,
            group_by="ticker",
            threads=True,
            progress=False,
            auto_adjust=False,
        )

    # =========================================================
    # LIVE PRICE
    # =========================================================

    def live_price(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        ticker = self.ticker(
            symbol
        )

        info = self._execute(
            lambda: ticker.fast_info
        )

        return {
            "symbol": symbol.upper(),
            "last_price": info.get(
                "lastPrice"
            ),
            "open": info.get(
                "open"
            ),
            "high": info.get(
                "dayHigh"
            ),
            "low": info.get(
                "dayLow"
            ),
            "volume": info.get(
                "lastVolume"
            ),
        }

    # =========================================================
    # COMPANY INFO
    # =========================================================

    def company_info(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).info
        )

    # =========================================================
    # FINANCIALS
    # =========================================================

    def financials(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).financials
        )

    def quarterly_financials(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).quarterly_financials
        )

    # =========================================================
    # BALANCE SHEET
    # =========================================================

    def balance_sheet(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).balance_sheet
        )

    def quarterly_balance_sheet(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).quarterly_balance_sheet
        )

    # =========================================================
    # CASH FLOW
    # =========================================================

    def cashflow(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).cashflow
        )

    def quarterly_cashflow(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).quarterly_cashflow
        )

    # =========================================================
    # EARNINGS
    # =========================================================

    def earnings(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).earnings
        )

    # =========================================================
    # DIVIDENDS
    # =========================================================

    def dividends(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).dividends
        )

    # =========================================================
    # SPLITS
    # =========================================================

    def splits(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).splits
        )

    # =========================================================
    # INSIDER TRANSACTIONS
    # =========================================================

    def insider_transactions(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).insider_transactions
        )

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    def recommendations(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).recommendations
        )

    # =========================================================
    # OPTIONS
    # =========================================================

    def option_expiries(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).options
        )

    def option_chain(
        self,
        symbol: str,
        expiry: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).option_chain(
                expiry
            )
        )

    # =========================================================
    # NEWS
    # =========================================================

    def news(
        self,
        symbol: str,
    ):

        try:

            return self._execute(
                lambda: self.ticker(
                    symbol
                ).news
            )

        except Exception:

            return []

    # =========================================================
    # HOLDERS
    # =========================================================

    def major_holders(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).major_holders
        )

    def institutional_holders(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).institutional_holders
        )

    def mutualfund_holders(
        self,
        symbol: str,
    ):

        return self._execute(
            lambda: self.ticker(
                symbol
            ).mutualfund_holders
        )

    # =========================================================
    # INDICES
    # =========================================================

    def nifty50(self):

        return self.historical_data(
            "^NSEI"
        )

    def banknifty(self):

        return self.historical_data(
            "^NSEBANK"
        )

    def sensex(self):

        return self.historical_data(
            "^BSESN"
        )

    def india_vix(self):

        return self.historical_data(
            "^INDIAVIX"
        )

    # =========================================================
    # HEALTH
    # =========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return {
            "provider": "yfinance",
            "version": self.VERSION,
            "installed": True,
        }

    def ping(
        self,
    ) -> bool:

        try:

            data = self.live_price(
                "RELIANCE"
            )

            return (
                data.get(
                    "last_price"
                )
                is not None
            )

        except Exception:

            logger.exception(
                "YFinance ping failed"
            )

            return False


# =============================================================
# SINGLETON
# =============================================================

yfinance_provider = (
    YahooFinanceProvider()
)


# =============================================================
# FACTORY
# =============================================================

def get_yfinance_provider(
) -> YahooFinanceProvider:

    return yfinance_provider