"""
TrendForge v2
Screener.in Provider

Purpose
-------
Fetch and normalize Indian equity fundamental data from
Screener.in.

This module is an adapter only.
It does NOT calculate trading signals or scores.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class ScreenerProvider:

    VERSION = "2.1"

    BASE_URL = "https://www.screener.in"

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
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        timeout: int = 15,
    ) -> None:

        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            self.HEADERS
        )

        self._cache: dict[
            str,
            tuple[Any, float],
        ] = {}

        self.cache_ttl = 300

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

    def _get_cache(
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
            > self.cache_ttl
        ):

            self._cache.pop(
                key,
                None,
            )

            return None

        return value

    def _set_cache(
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
        symbol: str,
    ) -> str:

        url = (
            f"{self.BASE_URL}"
            f"/company/"
            f"{symbol}/"
        )

        last_error = None

        for attempt in range(
            self.RETRIES
        ):

            try:

                response = (
                    self.session.get(
                        url,
                        timeout=self.timeout,
                    )
                )

                response.raise_for_status()

                return response.text

            except Exception as exc:

                last_error = exc

                logger.warning(
                    "Screener request failed "
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
            f"Screener request failed: "
            f"{last_error}"
        )

    # =========================================================
    # COMPANY PAGE
    # =========================================================

    def get_company(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        symbol = self.normalize_symbol(
            symbol
        )

        cached = self._get_cache(
            symbol
        )

        if cached is not None:
            return cached

        html = self._request(
            symbol
        )

        data = self._parse_company(
            symbol,
            html,
        )

        self._set_cache(
            symbol,
            data,
        )

        return data

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

        return company.get(
            "fundamentals",
            {},
        )

    def fundamentals(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        return self.get_fundamentals(
            symbol
        )

    # =========================================================
    # COMPANY PARSER
    # =========================================================

    def _parse_company(
        self,
        symbol: str,
        html: str,
    ) -> dict[str, Any]:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        result: dict[str, Any] = {
            "symbol": symbol,
            "source": "screener",
            "name": None,
            "fundamentals": {},
            "raw": {},
        }

        # -----------------------------------------------------
        # COMPANY NAME
        # -----------------------------------------------------

        title = soup.find(
            "h1"
        )

        if title:

            result["name"] = (
                title.get_text(
                    " ",
                    strip=True,
                )
            )

        # -----------------------------------------------------
        # KEY METRICS
        # -----------------------------------------------------

        metrics = {}

        for li in soup.select(
            "#top-ratios li"
        ):

            name_node = li.find(
                "span",
                class_="name",
            )

            value_node = li.find(
                "span",
                class_="number",
            )

            if (
                name_node
                and value_node
            ):

                name = (
                    name_node.get_text(
                        " ",
                        strip=True,
                    )
                )

                value = (
                    value_node.get_text(
                        " ",
                        strip=True,
                    )
                )

                metrics[
                    self._normalize_key(
                        name
                    )
                ] = self._number(
                    value
                )

        result[
            "fundamentals"
        ].update(
            metrics
        )

        # -----------------------------------------------------
        # DATA TABLES
        # -----------------------------------------------------

        tables = {}

        for table in soup.find_all(
            "table"
        ):

            table_name = (
                table.get(
                    "class"
                )
                or []
            )

            rows = []

            for row in table.find_all(
                "tr"
            ):

                cells = [
                    cell.get_text(
                        " ",
                        strip=True,
                    )
                    for cell in row.find_all(
                        ["th", "td"]
                    )
                ]

                if cells:
                    rows.append(
                        cells
                    )

            if rows:

                key = (
                    "_".join(
                        table_name
                    )
                    if table_name
                    else f"table_{len(tables)}"
                )

                tables[key] = rows

        result["raw"][
            "tables"
        ] = tables

        # -----------------------------------------------------
        # SHAREHOLDING
        # -----------------------------------------------------

        result[
            "shareholding"
        ] = self._parse_shareholding(
            soup
        )

        # -----------------------------------------------------
        # COMPANY DETAILS
        # -----------------------------------------------------

        result[
            "company_details"
        ] = self._parse_company_details(
            soup
        )

        return result

    # =========================================================
    # SHAREHOLDING
    # =========================================================

    def _parse_shareholding(
        self,
        soup: BeautifulSoup,
    ) -> dict[str, Any]:

        result = {}

        section = soup.find(
            id="shareholding"
        )

        if section is None:
            return result

        for row in section.find_all(
            "tr"
        ):

            cells = [
                cell.get_text(
                    " ",
                    strip=True,
                )
                for cell in row.find_all(
                    ["th", "td"]
                )
            ]

            if len(cells) < 2:
                continue

            key = self._normalize_key(
                cells[0]
            )

            result[key] = [
                self._number(
                    value
                )
                for value in cells[1:]
            ]

        return result

    # =========================================================
    # COMPANY DETAILS
    # =========================================================

    def _parse_company_details(
        self,
        soup: BeautifulSoup,
    ) -> dict[str, Any]:

        result = {}

        for item in soup.select(
            ".company-info li"
        ):

            text = item.get_text(
                " ",
                strip=True,
            )

            if ":" not in text:
                continue

            key, value = (
                text.split(
                    ":",
                    1,
                )
            )

            result[
                self._normalize_key(
                    key
                )
            ] = value.strip()

        return result

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        query: str,
    ) -> list[dict[str, str]]:

        query = str(
            query
        ).strip()

        if not query:
            return []

        url = (
            f"{self.BASE_URL}"
            f"/search/"
        )

        try:

            response = (
                self.session.get(
                    url,
                    params={
                        "q": query
                    },
                    timeout=self.timeout,
                )
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            results = []

            for link in soup.select(
                "a[href*='/company/']"
            ):

                href = link.get(
                    "href",
                    "",
                )

                name = link.get_text(
                    " ",
                    strip=True,
                )

                match = re.search(
                    r"/company/([^/]+)/",
                    href,
                )

                if not match:
                    continue

                results.append(
                    {
                        "symbol": match.group(
                            1
                        ).upper(),
                        "name": name,
                    }
                )

            # Deduplicate.

            unique = {}

            for item in results:

                unique[
                    item["symbol"]
                ] = item

            return list(
                unique.values()
            )

        except Exception as exc:

            logger.warning(
                "Screener search failed: %s",
                exc,
            )

            return []

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
    def _number(
        value: Any,
    ) -> float | None:

        if value is None:
            return None

        if isinstance(
            value,
            bool,
        ):
            return None

        if isinstance(
            value,
            (int, float),
        ):

            return float(value)

        text = str(
            value
        ).strip()

        if not text:
            return None

        negative = (
            text.startswith("(")
            and text.endswith(")")
        )

        text = (
            text.replace(
                ",",
                "",
            )
            .replace(
                "%",
                "",
            )
            .replace(
                "₹",
                "",
            )
            .replace(
                "Rs.",
                "",
            )
            .strip(
                "()"
            )
        )

        try:

            number = float(
                text
            )

            return (
                -number
                if negative
                else number
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    # =========================================================
    # HEALTH
    # =========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return {
            "provider": "screener",
            "version": self.VERSION,
            "base_url": self.BASE_URL,
            "available": True,
        }

    def ping(
        self,
    ) -> bool:

        try:

            response = (
                self.session.get(
                    self.BASE_URL,
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
# FACTORY
# =============================================================

screener_provider = (
    ScreenerProvider()
)


def get_screener_provider(
) -> ScreenerProvider:

    return screener_provider