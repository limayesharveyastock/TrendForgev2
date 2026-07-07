"""
providers/kite_provider.py

Centralized Kite Provider
-------------------------
Handles all communication with Zerodha Kite APIs.

Used by:
- scanner_engine
- trade_executor
- portfolio_manager
- risk_manager
- strategy_engine
"""

from __future__ import annotations

import logging
import threading
import time
from functools import wraps
from typing import Dict, List, Optional, Any

from kiteconnect import KiteConnect, KiteException

from config.settings import settings

logger = logging.getLogger(__name__)


class KiteProvider:
    """
    Singleton wrapper around KiteConnect.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):

        if hasattr(self, "_initialized"):
            return

        self.api_key = settings.KITE_API_KEY
        self.api_secret = settings.KITE_API_SECRET
        self.access_token = None

        self.kite = KiteConnect(api_key=self.api_key)

        self._initialized = True

    # -------------------------------------------------------------

    def set_access_token(self, access_token: str):
        self.access_token = access_token
        self.kite.set_access_token(access_token)

    # -------------------------------------------------------------

    def login_url(self) -> str:
        return self.kite.login_url()

    # -------------------------------------------------------------

    def generate_session(self, request_token: str):

        data = self.kite.generate_session(
            request_token=request_token,
            api_secret=self.api_secret
        )

        token = data["access_token"]

        self.set_access_token(token)

        return data

    # -------------------------------------------------------------

    def is_logged_in(self) -> bool:

        try:
            self.kite.profile()
            return True

        except Exception:
            return False

    # -------------------------------------------------------------

    def profile(self):

        return self.kite.profile()

    # -------------------------------------------------------------

    def margins(self):

        return self.kite.margins()

    # -------------------------------------------------------------

    def holdings(self):

        return self.kite.holdings()

    # -------------------------------------------------------------

    def positions(self):

        return self.kite.positions()

    # -------------------------------------------------------------

    def orders(self):

        return self.kite.orders()

    # -------------------------------------------------------------

    def trades(self):

        return self.kite.trades()

    # -------------------------------------------------------------

    def instruments(self, exchange=None):

        return self.kite.instruments(exchange)

    # -------------------------------------------------------------

    def ltp(self, instruments):

        return self.kite.ltp(instruments)

    # -------------------------------------------------------------

    def quote(self, instruments):

        return self.kite.quote(instruments)

    # -------------------------------------------------------------

    def historical_data(
            self,
            instrument_token,
            from_date,
            to_date,
            interval,
            continuous=False,
            oi=False
    ):

        return self.kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
            continuous=continuous,
            oi=oi
        )

    # -------------------------------------------------------------

    def place_order(
            self,
            exchange,
            tradingsymbol,
            transaction_type,
            quantity,
            order_type,
            product,
            variety="regular",
            price=None,
            trigger_price=None,
            validity="DAY",
            disclosed_quantity=None,
            tag=None
    ):

        return self.kite.place_order(
            variety=variety,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=order_type,
            product=product,
            price=price,
            trigger_price=trigger_price,
            validity=validity,
            disclosed_quantity=disclosed_quantity,
            tag=tag
        )

    # -------------------------------------------------------------

    def modify_order(
            self,
            variety,
            order_id,
            **kwargs
    ):

        return self.kite.modify_order(
            variety=variety,
            order_id=order_id,
            **kwargs
        )

    # -------------------------------------------------------------

    def cancel_order(
            self,
            variety,
            order_id
    ):

        return self.kite.cancel_order(
            variety=variety,
            order_id=order_id
        )

    # -------------------------------------------------------------

    def order_history(self, order_id):

        return self.kite.order_history(order_id)

    # -------------------------------------------------------------

    def order_trades(self, order_id):

        return self.kite.order_trades(order_id)

    # -------------------------------------------------------------

    def get_gtts(self):

        return self.kite.get_gtts()

    # -------------------------------------------------------------

    def invalidate_session(self):

        try:

            self.kite.invalidate_access_token()

            self.access_token = None

            logger.info("Kite session invalidated.")

        except Exception as e:

            logger.exception(e)

    # -------------------------------------------------------------

    def retry(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            retries = 3

            delay = 1

            for attempt in range(retries):

                try:

                    return func(*args, **kwargs)

                except KiteException as e:

                    logger.warning(
                        "Kite Exception (%s): %s",
                        attempt + 1,
                        e
                    )

                    if attempt == retries - 1:
                        raise

                    time.sleep(delay)

                    delay *= 2

                except Exception:

                    raise

        return wrapper

    # -------------------------------------------------------------

    @retry
    def safe_quote(self, instruments):

        return self.quote(instruments)

    # -------------------------------------------------------------

    @retry
    def safe_ltp(self, instruments):

        return self.ltp(instruments)

    # -------------------------------------------------------------

    @retry
    def safe_historical(
            self,
            instrument_token,
            from_date,
            to_date,
            interval,
            continuous=False,
            oi=False
    ):

        return self.historical_data(
            instrument_token,
            from_date,
            to_date,
            interval,
            continuous,
            oi
        )


kite_provider = KiteProvider()