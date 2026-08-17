"""
TrendForge v2
Kite Market Data Provider

Responsibilities
----------------
- KiteConnect authentication
- Historical OHLCV
- Live quotes
- Instruments
- Positions
- Orders
- Holdings
- LTP
- OHLC
- Normalized DataFrame output
- Retry handling
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping

import pandas as pd

try:
    from kiteconnect import KiteConnect
except ImportError:
    KiteConnect = None


logger = logging.getLogger(__name__)


class KiteProvider:
    """
    Single Kite provider.

    This intentionally replaces the duplicate class definitions
    previously present in the repository.
    """

    VERSION = "2.1"

    RETRIES = 3
    RETRY_DELAY = 1.0

    _instance = None
    _lock = threading.Lock()

    def __new__(
        cls,
        *args: Any,
        **kwargs: Any,
    ):
        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:

                    cls._instance = super().__new__(
                        cls
                    )

        return cls._instance

    def __init__(
        self,
        api_key: str | None = None,
        access_token: str | None = None,
    ) -> None:

        if getattr(
            self,
            "_initialized",
            False,
        ):
            if api_key:
                self.api_key = api_key

            if access_token:
                self.access_token = access_token

            return

        self.api_key = api_key
        self.access_token = access_token

        self.client = None

        self._initialized = True

        self._create_client()

    # =========================================================
    # CLIENT
    # =========================================================

    def _create_client(self) -> None:

        if KiteConnect is None:

            logger.warning(
                "kiteconnect is not installed."
            )

            self.client = None

            return

        if not self.api_key:

            logger.warning(
                "Kite API key not configured."
            )

            return

        try:

            self.client = KiteConnect(
                api_key=self.api_key
            )

            if self.access_token:

                self.client.set_access_token(
                    self.access_token
                )

        except Exception:

            logger.exception(
                "Failed to initialize Kite client"
            )

            self.client = None

    # =========================================================
    # AUTH
    # =========================================================

    def configure(
        self,
        api_key: str,
        access_token: str | None = None,
    ) -> "KiteProvider":

        self.api_key = api_key
        self.access_token = access_token

        self._create_client()

        return self

    def set_access_token(
        self,
        access_token: str,
    ) -> None:

        self.access_token = access_token

        if self.client is not None:

            self.client.set_access_token(
                access_token
            )

    def login_url(self) -> str | None:

        if self.client is None:
            return None

        return self.client.login_url()

    # =========================================================
    # AUTH CHECK
    # =========================================================

    def authenticated(self) -> bool:

        return bool(
            self.client is not None
            and self.access_token
        )

    def profile(self) -> dict[str, Any]:

        self._require_client()

        return self.client.profile()

    # =========================================================
    # SAFE CLIENT
    # =========================================================

    def _require_client(self):

        if self.client is None:

            raise RuntimeError(
                "Kite client is not initialized. "
                "Configure api_key and access_token."
            )

        if not self.access_token:

            raise RuntimeError(
                "Kite access token is not configured."
            )

        return self.client

    # =========================================================
    # RETRY
    # =========================================================

    def _execute(
        self,
        method: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

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

                if attempt >= self.RETRIES - 1:
                    break

                delay = (
                    self.RETRY_DELAY
                    * (2 ** attempt)
                )

                logger.warning(
                    "Kite request failed "
                    "(%s/%s): %s",
                    attempt + 1,
                    self.RETRIES,
                    exc,
                )

                time.sleep(delay)

        raise last_error

    # =========================================================
    # HISTORICAL DATA
    # =========================================================

    def historical_data(
        self,
        instrument_token: int | str,
        from_date: Any,
        to_date: Any,
        interval: str = "day",
        continuous: bool = False,
        oi: bool = False,
    ) -> pd.DataFrame:

        client = self._require_client()

        records = self._execute(
            client.historical_data,
            instrument_token,
            from_date,
            to_date,
            interval,
            continuous=continuous,
            oi=oi,
        )

        return self._normalize_candles(
            records
        )

    def candles(
        self,
        instrument_token: int | str,
        days: int = 365,
        interval: str = "day",
        oi: bool = False,
    ) -> pd.DataFrame:

        to_date = datetime.now()

        from_date = (
            to_date
            - timedelta(days=days)
        )

        return self.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
            oi=oi,
        )

    # =========================================================
    # SYMBOL CANDLES
    # =========================================================

    def symbol_candles(
        self,
        instrument_token: int | str,
        period: str = "1y",
        interval: str = "day",
        oi: bool = False,
    ) -> pd.DataFrame:

        days_map = {
            "1d": 2,
            "5d": 7,
            "1mo": 31,
            "3mo": 100,
            "6mo": 190,
            "1y": 370,
            "2y": 740,
            "5y": 1850,
        }

        days = days_map.get(
            period,
            365,
        )

        return self.candles(
            instrument_token=instrument_token,
            days=days,
            interval=interval,
            oi=oi,
        )

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_candles(
        records: Any,
    ) -> pd.DataFrame:

        if records is None:

            return pd.DataFrame(
                columns=[
                    "date",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]
            )

        df = pd.DataFrame(
            records
        )

        if df.empty:
            return df

        rename_map = {
            "timestamp": "date",
            "oi": "open_interest",
        }

        df.rename(
            columns=rename_map,
            inplace=True,
        )

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce",
            )

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                )

        required = [
            "open",
            "high",
            "low",
            "close",
        ]

        existing = [
            column
            for column in required
            if column in df.columns
        ]

        if existing:

            df = df.dropna(
                subset=existing
            )

        if "date" in df.columns:

            df = df.sort_values(
                "date"
            )

            df = df.drop_duplicates(
                subset=["date"],
                keep="last",
            )

        df.reset_index(
            drop=True,
            inplace=True,
        )

        return df

    # =========================================================
    # LTP
    # =========================================================

    def ltp(
        self,
        instruments: str | Iterable[str],
    ) -> dict[str, Any]:

        client = self._require_client()

        if isinstance(
            instruments,
            str,
        ):
            instruments = [
                instruments
            ]

        return self._execute(
            client.ltp,
            list(instruments),
        )

    # =========================================================
    # QUOTE
    # =========================================================

    def quote(
        self,
        instruments: str | Iterable[str],
    ) -> dict[str, Any]:

        client = self._require_client()

        if isinstance(
            instruments,
            str,
        ):
            instruments = [
                instruments
            ]

        return self._execute(
            client.quote,
            list(instruments),
        )

    # =========================================================
    # OHLC
    # =========================================================

    def ohlc(
        self,
        instruments: str | Iterable[str],
    ) -> dict[str, Any]:

        client = self._require_client()

        if isinstance(
            instruments,
            str,
        ):
            instruments = [
                instruments
            ]

        return self._execute(
            client.ohlc,
            list(instruments),
        )

    # =========================================================
    # INSTRUMENTS
    # =========================================================

    def instruments(
        self,
        exchange: str | None = None,
    ) -> list[dict[str, Any]]:

        client = self._require_client()

        if exchange:

            return self._execute(
                client.instruments,
                exchange,
            )

        return self._execute(
            client.instruments
        )

    def instruments_dataframe(
        self,
        exchange: str | None = None,
    ) -> pd.DataFrame:

        return pd.DataFrame(
            self.instruments(
                exchange
            )
        )

    # =========================================================
    # ORDERS
    # =========================================================

    def orders(self) -> list[dict[str, Any]]:

        client = self._require_client()

        return self._execute(
            client.orders
        )

    def order_history(
        self,
        order_id: str,
    ) -> list[dict[str, Any]]:

        client = self._require_client()

        return self._execute(
            client.order_history,
            order_id,
        )

    # =========================================================
    # POSITIONS
    # =========================================================

    def positions(self) -> dict[str, Any]:

        client = self._require_client()

        return self._execute(
            client.positions
        )

    # =========================================================
    # HOLDINGS
    # =========================================================

    def holdings(self) -> list[dict[str, Any]]:

        client = self._require_client()

        return self._execute(
            client.holdings
        )

    # =========================================================
    # MARGINS
    # =========================================================

    def margins(self) -> dict[str, Any]:

        client = self._require_client()

        return self._execute(
            client.margins
        )

    # =========================================================
    # TRADES
    # =========================================================

    def trades(self) -> list[dict[str, Any]]:

        client = self._require_client()

        return self._execute(
            client.trades
        )

    # =========================================================
    # MARKET DEPTH
    # =========================================================

    def market_depth(
        self,
        instrument: str,
    ) -> dict[str, Any]:

        return self.quote(
            instrument
        )

    # =========================================================
    # HEALTH
    # =========================================================

    def health(self) -> dict[str, Any]:

        return {
            "provider": "kite",
            "version": self.VERSION,
            "installed": KiteConnect is not None,
            "configured": self.client is not None,
            "authenticated": self.authenticated(),
        }

    def ping(self) -> bool:

        if not self.authenticated():
            return False

        try:

            self.profile()

            return True

        except Exception:

            logger.exception(
                "Kite ping failed"
            )

            return False


# =============================================================
# SINGLETON
# =============================================================

kite_provider = KiteProvider()


# =============================================================
# FACTORY
# =============================================================

def get_kite_provider(
    api_key: str | None = None,
    access_token: str | None = None,
) -> KiteProvider:

    if api_key or access_token:

        kite_provider.configure(
            api_key=api_key or kite_provider.api_key,
            access_token=access_token
            or kite_provider.access_token,
        )

    return kite_provider