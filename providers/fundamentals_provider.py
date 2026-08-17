"""
TrendForge v2
Fundamentals Provider

Normalized fundamental-data interface.

Priority:
    Tijori -> Screener -> YFinance

The provider does NOT generate trading signals.
It only collects and normalizes fundamental data.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any


logger = logging.getLogger(__name__)


@dataclass
class FundamentalSnapshot:
    symbol: str

    market_cap: float | None = None
    pe: float | None = None
    pb: float | None = None
    dividend_yield: float | None = None

    revenue: float | None = None
    revenue_growth: float | None = None

    earnings: float | None = None
    earnings_growth: float | None = None

    eps: float | None = None
    roe: float | None = None
    roce: float | None = None

    debt_to_equity: float | None = None
    current_ratio: float | None = None

    operating_margin: float | None = None
    net_margin: float | None = None

    book_value: float | None = None

    promoter_holding: float | None = None
    institutional_holding: float | None = None
    mutual_fund_holding: float | None = None

    source: str = "unknown"

    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FundamentalsProvider:

    VERSION = "2.1"

    def __init__(
        self,
        tijori: Any = None,
        screener: Any = None,
        yfinance: Any = None,
    ) -> None:

        self.tijori = tijori
        self.screener = screener
        self.yfinance = yfinance

    # =========================================================
    # PUBLIC API
    # =========================================================

    def get(
        self,
        symbol: str,
    ) -> FundamentalSnapshot:

        symbol = self._normalize_symbol(
            symbol
        )

        # -----------------------------------------------------
        # 1. TIJORI
        # -----------------------------------------------------

        if self.tijori is not None:

            try:

                data = self._fetch(
                    self.tijori,
                    symbol,
                )

                if data:

                    return self._normalize(
                        symbol,
                        data,
                        "tijori",
                    )

            except Exception as exc:

                logger.warning(
                    "Tijori fundamentals failed "
                    "for %s: %s",
                    symbol,
                    exc,
                )

        # -----------------------------------------------------
        # 2. SCREENER
        # -----------------------------------------------------

        if self.screener is not None:

            try:

                data = self._fetch(
                    self.screener,
                    symbol,
                )

                if data:

                    return self._normalize(
                        symbol,
                        data,
                        "screener",
                    )

            except Exception as exc:

                logger.warning(
                    "Screener fundamentals failed "
                    "for %s: %s",
                    symbol,
                    exc,
                )

        # -----------------------------------------------------
        # 3. YFINANCE
        # -----------------------------------------------------

        if self.yfinance is not None:

            try:

                method = getattr(
                    self.yfinance,
                    "company_info",
                    None,
                )

                if callable(method):

                    data = method(
                        symbol
                    )

                    if data:

                        return self._normalize(
                            symbol,
                            data,
                            "yfinance",
                        )

            except Exception as exc:

                logger.warning(
                    "YFinance fundamentals failed "
                    "for %s: %s",
                    symbol,
                    exc,
                )

        # -----------------------------------------------------
        # NO PROVIDER
        # -----------------------------------------------------

        return FundamentalSnapshot(
            symbol=symbol,
            source="unavailable",
        )

    # =========================================================
    # FETCH
    # =========================================================

    @staticmethod
    def _fetch(
        provider: Any,
        symbol: str,
    ) -> Any:

        for method_name in (
            "get_fundamentals",
            "fundamentals",
            "company_info",
        ):

            method = getattr(
                provider,
                method_name,
                None,
            )

            if callable(method):

                return method(
                    symbol
                )

        raise AttributeError(
            "Fundamental provider has no "
            "supported fundamentals method"
        )

    # =========================================================
    # NORMALIZATION
    # =========================================================

    def _normalize(
        self,
        symbol: str,
        data: Any,
        source: str,
    ) -> FundamentalSnapshot:

        if isinstance(
            data,
            FundamentalSnapshot,
        ):

            data.symbol = symbol
            data.source = source

            return data

        if not isinstance(
            data,
            dict,
        ):

            try:

                data = dict(data)

            except Exception:

                data = {}

        flat = self._flatten(
            data
        )

        return FundamentalSnapshot(
            symbol=symbol,

            market_cap=self._number(
                self._find(
                    flat,
                    "market_cap",
                    "marketcap",
                    "marketCapitalization",
                )
            ),

            pe=self._number(
                self._find(
                    flat,
                    "pe",
                    "pe_ratio",
                    "trailing_pe",
                    "trailingPE",
                )
            ),

            pb=self._number(
                self._find(
                    flat,
                    "pb",
                    "pb_ratio",
                    "price_to_book",
                    "priceToBook",
                )
            ),

            dividend_yield=self._number(
                self._find(
                    flat,
                    "dividend_yield",
                    "dividendYield",
                )
            ),

            revenue=self._number(
                self._find(
                    flat,
                    "revenue",
                    "total_revenue",
                    "totalRevenue",
                )
            ),

            revenue_growth=self._number(
                self._find(
                    flat,
                    "revenue_growth",
                    "revenueGrowth",
                )
            ),

            earnings=self._number(
                self._find(
                    flat,
                    "earnings",
                    "net_income",
                    "netIncome",
            )
            ),

            earnings_growth=self._number(
                self._find(
                    flat,
                    "earnings_growth",
                    "earningsGrowth",
                    "profit_growth",
                )
            ),

            eps=self._number(
                self._find(
                    flat,
                    "eps",
                    "trailing_eps",
                    "trailingEps",
                )
            ),

            roe=self._number(
                self._find(
                    flat,
                    "roe",
                    "return_on_equity",
                    "returnOnEquity",
                )
            ),

            roce=self._number(
                self._find(
                    flat,
                    "roce",
                    "return_on_capital",
                )
            ),

            debt_to_equity=self._number(
                self._find(
                    flat,
                    "debt_to_equity",
                    "debtToEquity",
                )
            ),

            current_ratio=self._number(
                self._find(
                    flat,
                    "current_ratio",
                    "currentRatio",
                )
            ),

            operating_margin=self._number(
                self._find(
                    flat,
                    "operating_margin",
                    "operatingMargins",
                )
            ),

            net_margin=self._number(
                self._find(
                    flat,
                    "net_margin",
                    "profit_margin",
                    "profitMargins",
                )
            ),

            book_value=self._number(
                self._find(
                    flat,
                    "book_value",
                    "bookValue",
                )
            ),

            promoter_holding=self._number(
                self._find(
                    flat,
                    "promoter_holding",
                    "promoterHolding",
                )
            ),

            institutional_holding=self._number(
                self._find(
                    flat,
                    "institutional_holding",
                    "institutionalHolding",
                )
            ),

            mutual_fund_holding=self._number(
                self._find(
                    flat,
                    "mutual_fund_holding",
                    "mutualFundHolding",
                )
            ),

            source=source,

            raw=data,
        )

    # =========================================================
    # FLATTEN
    # =========================================================

    @classmethod
    def _flatten(
        cls,
        data: dict[str, Any],
        prefix: str = "",
    ) -> dict[str, Any]:

        result: dict[str, Any] = {}

        for key, value in data.items():

            normalized_key = (
                str(key)
                .strip()
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

            full_key = (
                f"{prefix}_{normalized_key}"
                if prefix
                else normalized_key
            )

            if isinstance(
                value,
                dict,
            ):

                result.update(
                    cls._flatten(
                        value,
                        full_key,
                    )
                )

            else:

                result[normalized_key] = value
                result[full_key] = value

        return result

    # =========================================================
    # FIND VALUE
    # =========================================================

    @staticmethod
    def _find(
        data: dict[str, Any],
        *keys: str,
    ) -> Any:

        for key in keys:

            normalized = (
                key.lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

            if normalized in data:

                return data[
                    normalized
                ]

        return None

    # =========================================================
    # NUMBER
    # =========================================================

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

        try:

            text = (
                str(value)
                .strip()
                .replace(",", "")
                .replace("%", "")
            )

            if not text:
                return None

            return float(text)

        except (
            TypeError,
            ValueError,
        ):

            return None

    # =========================================================
    # SYMBOL
    # =========================================================

    @staticmethod
    def _normalize_symbol(
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

                return symbol[
                    :-len(suffix)
                ]

        return symbol

    # =========================================================
    # HEALTH
    # =========================================================

    def health(
        self,
    ) -> dict[str, Any]:

        return {
            "provider": "fundamentals",
            "version": self.VERSION,
            "tijori": self.tijori is not None,
            "screener": self.screener is not None,
            "yfinance": self.yfinance is not None,
        }


# =============================================================
# FACTORY
# =============================================================

def create_fundamentals_provider(
    tijori: Any = None,
    screener: Any = None,
    yfinance: Any = None,
) -> FundamentalsProvider:

    return FundamentalsProvider(
        tijori=tijori,
        screener=screener,
        yfinance=yfinance,
    )