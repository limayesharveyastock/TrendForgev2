"""
TrendForge v2
Tijori Finance Provider

Adapter for Tijori Finance fundamental / ownership data.

Responsibilities:
- company fundamentals
- valuation
- profitability
- growth
- leverage
- shareholding
- institutional ownership
- raw provider response

This module does NOT calculate TrendForge scores.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import requests


logger = logging.getLogger(__name__)


class TijoriProvider:

    VERSION = "2.1"

    BASE_URL = "https://www.tijorifinance.com"

    RETRIES = 3
    RETRY_DELAY = 1.0
    CACHE_TTL = 300
    TIMEOUT = 15

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = TIMEOUT,
    ) -> None:

        self.base_url = (
            base_url.rstrip("/")
            if base_url
            else self.BASE_URL
        )

        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            self.HEADERS
        )

        self._cache: dict[
            str,
            tuple[Any, float],
        ] = {}

    # =========================================================
    # SYMBOL
    # =========================================================

    @staticmethod
    def normalize_symbol(
        symbol: str,
    ) -> str:

        symbol = str(
            symbol
        ).strip().upper()

        for suffix in (
            ".NS",
            ".BO",
        ):

            if symbol.endswith(
                suffix
            ):

                symbol = symbol[
                    :-len(suffix)
                ]

        return symbol

    # =========================================================
    # CACHE
    # =========================================================

    def _cache_get(
        self,
        key: str,
    ) -> Any:

        item = self._cache.get(
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

            self._cache.pop(
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

        self._cache[key] = (
            value,
            time.time(),
        )

    def clear_cache(self) -> None:

        self._cache.clear()

    # =========================================================
    # HTTP
    # =========================================================

    def _request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> Any:

        last_error = None

        for attempt in range(
            self.RETRIES
        ):

            try:

                response = (
                    self.session.get(
                        url,
                        params=params,
                        timeout=self.timeout,
                    )
                )

                response.raise_for_status()

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    ).lower()
                )

                if (
                    "json"
                    in content_type
                ):

                    return response.json()

                return response.text

            except Exception as exc:

                last_error = exc

                logger.warning(
                    "Tijori request failed "
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
                        * (attempt + 1)
                    )

        raise RuntimeError(
            f"Tijori request failed: "
            f"{last_error}"
        )

    # =========================================================
    # COMPANY
    # =========================================================

    def get_company(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        symbol = self.normalize_symbol(
            symbol
        )

        cache_key = (
            f"company:{symbol}"
        )

        cached = self._cache_get(
            cache_key
        )

        if cached is not None:
            return cached

        url = (
            f"{self.base_url}"
            f"/company/"
            f"{symbol}"
        )

        try:

            data = self._request(
                url
            )

        except Exception as exc:

            logger.warning(
                "Tijori company lookup failed "
                "for %s: %s",
                symbol,
                exc,
            )

            data = {}

        result = self._normalize_response(
            symbol,
            data,
        )

        self._cache_set(
            cache_key,
            result,
        )

        return result

    # =========================================================
    # FUNDAMENTALS
    # =========================================================

    def get_fundamentals(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        company = self.get_company(
            symbol
        )

        if "fundamentals" in company:

            return company[
                "fundamentals"
            ]

        return company

    def fundamentals(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        return self.get_fundamentals(
            symbol
        )

    # =========================================================
    # VALUATION
    # =========================================================

    def valuation(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        data = self.get_company(
            symbol
        )

        return data.get(
            "valuation",
            {},
        )

    # =========================================================
    # PROFITABILITY
    # =========================================================

    def profitability(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        data = self.get_company(
            symbol
        )

        return data.get(
            "profitability",
            {},
        )

    # =========================================================
    # GROWTH
    # =========================================================

    def growth(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        data = self.get_company(
            symbol
        )

        return data.get(
            "growth",
            {},
        )

    # =========================================================
    # LEVERAGE
    # =========================================================

    def leverage(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        data = self.get_company(
            symbol
        )

        return data.get(
            "leverage",
            {},
        )

    # =========================================================
    # SHAREHOLDING
    # =========================================================

    def shareholding(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        data = self.get_company(
            symbol
        )

        return data.get(
            "shareholding",
            {},
        )

    # =========================================================
    # INSTITUTIONAL HOLDING
    # =========================================================

    def institutional_holding(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        holding = self.shareholding(
            symbol
        )

        result = {}

        for key, value in holding.items():

            key_normalized = (
                str(key)
                .lower()
            )

            if any(
                term in key_normalized
                for term in (
                    "institution",
                    "mutual",
                    "fii",
                    "dii",
                    "foreign",
                )
            ):

                result[key] = value

        return result

    # =========================================================
    # NORMALIZATION
    # =========================================================

    def _normalize_response(
        self,
        symbol: str,
        data: Any,
    ) -> dict[str, Any]:

        if not isinstance(
            data,
            dict,
        ):

            return {
                "symbol": symbol,
                "source": "tijori",
                "raw": data,
            }

        result = {
            "symbol": symbol,
            "source": "tijori",
            "fundamentals": {},
            "valuation": {},
            "profitability": {},
            "growth": {},
            "leverage": {},
            "shareholding": {},
            "raw": data,
        }

        # Preserve already normalized structures.

        for section in (
            "fundamentals",
            "valuation",
            "profitability",
            "growth",
            "leverage",
            "shareholding",
        ):

            value = data.get(
                section
            )

            if isinstance(
                value,
                dict,
            ):

                result[
                    section
                ] = self._normalize_dict(
                    value
                )

        # Also flatten top-level values into
        # fundamentals when a structured response
        # is not supplied.

        for key, value in data.items():

            normalized = (
                self._normalize_key(
                    key
                )
            )

            if normalized in (
                "valuation",
                "profitability",
                "growth",
                "leverage",
                "shareholding",
                "fundamentals",
            ):

                continue

            result[
                "fundamentals"
            ][normalized] = (
                self._convert_value(
                    value
                )
            )

        return result

    # =========================================================
    # NORMALIZE DICT
    # =========================================================

    def _normalize_dict(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        result = {}

        for key, value in data.items():

            normalized = (
                self._normalize_key(
                    key
                )
            )

            if isinstance(
                value,
                dict,
            ):

                result[
                    normalized
                ] = self._normalize_dict(
                    value
                )

            elif isinstance(
                value,
                list,
            ):

                result[
                    normalized
                ] = [
                    self._convert_value(
                        item
                    )
                    for item in value
                ]

            else:

                result[
                    normalized
                ] = self._convert_value(
                    value
                )

        return result

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _normalize_key(
        value: str,
    ) -> str:

        value = str(
            value
        ).strip().lower()

        value = re.sub(
            r"[^a-z0-9]+",
            "_",
            value,
        )

        return value.strip(
            "_"
        )

    @staticmethod
    def _convert_value(
        value: Any,
    ) -> Any:

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            (int, float),
        ):
            return float(value)

        if not isinstance(
            value,
            str,
        ):
            return value

        text = (
            value
            .strip()
            .replace(
                ",",
                "",
            )
            .replace(
                "₹",
                "",
            )
        )

        if not text:
            return None

        percent = text.endswith(
            "%"
        )

        if percent:

            text = text[:-1].strip()

        try:

            number = float(
                text
            )

            return number

        except (
            TypeError,
            ValueError,
        ):

            return value

    # =========================================================
    # HEALTH
    # =========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return {
            "provider": "tijori",
            "version": self.VERSION,
            "base_url": self.base_url,
            "available": True,
        }

    def ping(
        self,
    ) -> bool:

        try:

            response = (
                self.session.get(
                    self.base_url,
                    timeout=self.timeout,
                )
            )

            return (
                response.status_code
                == 200
            )

        except Exception:

            return False


# =============================================================
# SINGLETON
# =============================================================

tijori_provider = (
    TijoriProvider()
)


# =============================================================
# FACTORY
# =============================================================

def get_tijori_provider(
) -> TijoriProvider:

    return tijori_provider