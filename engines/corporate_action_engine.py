"""
TrendForge v2 - Corporate Action & Event Engine

Purpose
-------
Evaluates corporate events that can materially affect short-term and
swing-trading decisions.

Covered events
--------------
- Results / earnings
- Dividend
- Bonus
- Split
- Rights issue
- Buyback
- Merger / demerger
- Acquisition / divestment
- Fund raising
- Preferential issue
- QIP
- OFS
- Promoter transactions
- Pledge / release of pledge
- Delisting / suspension
- Board meetings
- Regulatory / legal events
- Rating actions
- Order wins / cancellations

Principles
----------
1. Never invent an event.
2. Missing event data lowers confidence.
3. Event score is directional, not a standalone trade signal.
4. Near-term material events receive higher weight.
5. Negative hard-risk events can veto a BUY candidate.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from engines.base_engine import BaseEngine, EngineResult


class CorporateActionEngine(BaseEngine):
    NAME = "Corporate Action Engine"
    priority = 4
    mandatory = False

    MAX_POSITIVE = 65.0
    MAX_NEGATIVE = 100.0

    POSITIVE_TYPES = {
        "dividend": 5.0,
        "special_dividend": 7.0,
        "bonus": 4.0,
        "split": 2.0,
        "buyback": 8.0,
        "rights_issue": 2.0,
        "qip": 3.0,
        "fund_raise": 3.0,
        "order_win": 8.0,
        "large_order": 8.0,
        "acquisition": 5.0,
        "divestment": 4.0,
        "demerger": 4.0,
        "rating_upgrade": 5.0,
        "pledge_release": 6.0,
        "promoter_buy": 8.0,
        "board_approval": 2.0,
    }

    NEGATIVE_TYPES = {
        "earnings_miss": -12.0,
        "profit_warning": -15.0,
        "guidance_cut": -12.0,
        "dividend_cut": -8.0,
        "dividend_cancelled": -10.0,
        "dilution": -8.0,
        "preferential_issue": -5.0,
        "ofs": -6.0,
        "promoter_sell": -10.0,
        "pledge_increase": -12.0,
        "order_cancelled": -12.0,
        "order_loss": -10.0,
        "acquisition_risk": -5.0,
        "regulatory": -15.0,
        "legal": -15.0,
        "fraud": -30.0,
        "default": -30.0,
        "insolvency": -35.0,
        "bankruptcy": -40.0,
        "delisting": -35.0,
        "suspension": -40.0,
        "rating_downgrade": -12.0,
    }

    HARD_NEGATIVE = {
        "fraud",
        "default",
        "insolvency",
        "bankruptcy",
        "delisting",
        "suspension",
    }

    TYPE_ALIASES = {
        "results": "earnings",
        "quarterly_results": "earnings",
        "financial_results": "earnings",
        "earnings": "earnings",
        "dividend": "dividend",
        "special dividend": "special_dividend",
        "bonus": "bonus",
        "bonus issue": "bonus",
        "stock split": "split",
        "split": "split",
        "buyback": "buyback",
        "share buyback": "buyback",
        "rights": "rights_issue",
        "rights issue": "rights_issue",
        "qip": "qip",
        "fund raising": "fund_raise",
        "fundraise": "fund_raise",
        "preferential": "preferential_issue",
        "preferential issue": "preferential_issue",
        "ofs": "ofs",
        "offer for sale": "ofs",
        "merger": "merger",
        "demerger": "demerger",
        "acquisition": "acquisition",
        "divestment": "divestment",
        "order win": "order_win",
        "order": "order_win",
        "order cancellation": "order_cancelled",
        "order cancelled": "order_cancelled",
        "pledge": "pledge_increase",
        "pledge increase": "pledge_increase",
        "pledge release": "pledge_release",
        "promoter buy": "promoter_buy",
        "promoter purchase": "promoter_buy",
        "promoter sell": "promoter_sell",
        "rating upgrade": "rating_upgrade",
        "rating downgrade": "rating_downgrade",
        "regulatory": "regulatory",
        "legal": "legal",
        "fraud": "fraud",
        "default": "default",
        "insolvency": "insolvency",
        "bankruptcy": "bankruptcy",
        "delisting": "delisting",
        "suspension": "suspension",
    }

    POSITIVE_TERMS = (
        "order win",
        "large order",
        "major order",
        "contract win",
        "buyback",
        "special dividend",
        "dividend declared",
        "bonus declared",
        "rating upgrade",
        "pledge released",
        "promoter bought",
        "promoter purchase",
        "acquisition approved",
        "demerger approved",
        "fund raise approved",
    )

    NEGATIVE_TERMS = (
        "profit warning",
        "guidance cut",
        "order cancelled",
        "order cancellation",
        "rating downgrade",
        "pledge increased",
        "promoter sold",
        "fraud",
        "default",
        "insolvency",
        "bankruptcy",
        "delisting",
        "suspension",
        "regulatory action",
        "legal action",
    )

    def __init__(self, provider=None, repository=None):
        self.provider = provider
        self.repository = repository
        self._discover_dependencies()

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def evaluate(self, stock: Any) -> EngineResult:
        payload = self._normalise(stock)
        symbol = self._symbol(payload, stock)
        events = self._collect_events(symbol, payload)

        scored = []
        positive = 0.0
        negative = 0.0
        hard_block = False

        for event in events:
            item = self._score_event(event)
            scored.append(item)

            if item["score"] > 0:
                positive += item["score"]
            else:
                negative += abs(item["score"])

            if item["hard_negative"]:
                hard_block = True

        positive = min(self.MAX_POSITIVE, positive)
        negative = min(self.MAX_NEGATIVE, negative)

        raw_score = 50.0 + positive - negative
        score = self._clamp(raw_score, 0.0, 100.0)

        data_quality = self._data_quality(events)
        confidence = self._confidence(events, data_quality)
        bias = self._bias(positive, negative)

        reasons = self._reasons(scored)
        warnings = self._warnings(scored)

        if not events:
            warnings.append("No corporate-event data available.")

        passed = (
            score >= 55.0
            and not hard_block
        )

        return EngineResult(
            engine=self.NAME,
            passed=passed,
            score=round(score, 2),
            confidence=round(confidence, 2),
            grade=self._grade(score),
            reasons=self._dedupe(reasons)[:30],
            warnings=self._dedupe(warnings)[:30],
            metrics={
                "symbol": symbol,
                "event_count": len(events),
                "positive_event_score": round(positive, 2),
                "negative_event_score": round(negative, 2),
                "bias": bias,
                "hard_block": hard_block,
                "data_quality": data_quality,
                "events": scored[:50],
                "near_term_events": sum(
                    1 for e in scored
                    if e["time_bucket"] == "near_term"
                ),
                "material_events": sum(
                    1 for e in scored
                    if e["material"]
                ),
            },
        )

    # ------------------------------------------------------------------
    # DATA DISCOVERY
    # ------------------------------------------------------------------

    def _discover_dependencies(self):
        if self.provider is None:
            candidates = (
                ("providers.nse_provider", "NSEProvider"),
                ("providers.corporate_action_provider", "CorporateActionProvider"),
            )

            for module_name, class_name in candidates:
                try:
                    module = __import__(
                        module_name,
                        fromlist=[class_name],
                    )
                    cls = getattr(module, class_name, None)
                    if cls is not None:
                        self.provider = cls()
                        break
                except Exception:
                    continue

        if self.repository is None:
            try:
                from database.repositories.corporate_repository import (
                    CorporateRepository,
                )
                self.repository = CorporateRepository()
            except Exception:
                pass

    def _collect_events(
        self,
        symbol: str,
        payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        raw: List[Any] = []

        for key in (
            "corporate_actions",
            "corporate_events",
            "events",
            "corporate_action",
        ):
            value = payload.get(key)
            if value:
                raw.extend(self._rows(value))

        if self.provider is not None:
            for method_name in (
                "get_corporate_actions",
                "get_corporate_events",
                "get_events",
                "fetch_corporate_actions",
            ):
                method = getattr(self.provider, method_name, None)
                if not callable(method):
                    continue
                try:
                    value = method(symbol)
                    if value:
                        raw.extend(self._rows(value))
                        break
                except Exception:
                    continue

        if self.repository is not None:
            for method_name in (
                "get_by_symbol",
                "get_corporate_actions",
                "by_symbol",
            ):
                method = getattr(self.repository, method_name, None)
                if not callable(method):
                    continue
                try:
                    value = method(symbol)
                    if value:
                        raw.extend(self._rows(value))
                        break
                except Exception:
                    continue

        normalized = []
        seen = set()

        for row in raw:
            event = self._normalize_event(row)
            fingerprint = self._fingerprint(event)

            if fingerprint in seen:
                continue

            seen.add(fingerprint)
            normalized.append(event)

        return normalized

    # ------------------------------------------------------------------
    # NORMALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise(stock: Any) -> Dict[str, Any]:
        if isinstance(stock, Mapping):
            return dict(stock)

        if is_dataclass(stock):
            try:
                return asdict(stock)
            except Exception:
                pass

        if hasattr(stock, "__dict__"):
            try:
                return dict(vars(stock))
            except Exception:
                pass

        return {}

    @staticmethod
    def _symbol(
        payload: Dict[str, Any],
        stock: Any,
    ) -> str:
        if isinstance(stock, str):
            return stock.strip().upper()

        return str(
            payload.get("symbol")
            or payload.get("ticker")
            or payload.get("tradingsymbol")
            or ""
        ).strip().upper()

    @classmethod
    def _rows(cls, value: Any) -> List[Dict[str, Any]]:
        if value is None:
            return []

        if isinstance(value, Mapping):
            for key in (
                "data",
                "results",
                "items",
                "rows",
                "events",
                "corporate_actions",
            ):
                nested = value.get(key)
                if isinstance(nested, (list, tuple)):
                    return [
                        cls._to_dict(x)
                        for x in nested
                    ]
            return [dict(value)]

        if isinstance(value, (list, tuple, set)):
            return [
                cls._to_dict(x)
                for x in value
            ]

        return []

    @staticmethod
    def _to_dict(value: Any) -> Dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, Mapping):
            return dict(value)

        if is_dataclass(value):
            try:
                return asdict(value)
            except Exception:
                return {}

        if hasattr(value, "__dict__"):
            try:
                return dict(vars(value))
            except Exception:
                return {}

        return {}

    def _normalize_event(
        self,
        row: Mapping[str, Any],
    ) -> Dict[str, Any]:

        title = str(
            row.get("title")
            or row.get("headline")
            or row.get("description")
            or row.get("event")
            or row.get("name")
            or ""
        ).strip()

        raw_type = str(
            row.get("type")
            or row.get("event_type")
            or row.get("category")
            or ""
        ).strip().lower()

        event_type = self._canonical_type(
            raw_type,
            title,
        )

        event_date = self._event_date(row)

        ex_date = self._date_from(
            row.get("ex_date")
            or row.get("exDate")
        )

        record_date = self._date_from(
            row.get("record_date")
            or row.get("recordDate")
        )

        amount = self._number(
            row.get("amount")
            or row.get("value")
            or row.get("value_crore")
            or row.get("transaction_value")
        )

        percent = self._number(
            row.get("percent")
            or row.get("percentage")
            or row.get("change_percent")
        )

        status = str(
            row.get("status")
            or row.get("action")
            or ""
        ).strip().lower()

        return {
            "type": event_type,
            "title": title,
            "date": event_date,
            "ex_date": ex_date,
            "record_date": record_date,
            "amount": amount,
            "percent": percent,
            "status": status,
            "raw": dict(row),
        }

    def _canonical_type(
        self,
        raw_type: str,
        title: str,
    ) -> str:

        normalized = re.sub(
            r"\s+",
            " ",
            raw_type.lower().strip(),
        )

        if normalized in self.TYPE_ALIASES:
            return self.TYPE_ALIASES[normalized]

        text = f"{normalized} {title.lower()}"

        for alias, canonical in self.TYPE_ALIASES.items():
            if alias in text:
                return canonical

        if any(
            term in text
            for term in self.POSITIVE_TERMS
        ):
            if "buyback" in text:
                return "buyback"
            if "dividend" in text:
                return "dividend"
            if "pledge" in text:
                return "pledge_release"
            if "rating" in text:
                return "rating_upgrade"
            if "order" in text:
                return "order_win"

        if any(
            term in text
            for term in self.NEGATIVE_TERMS
        ):
            if "fraud" in text:
                return "fraud"
            if "default" in text:
                return "default"
            if "insolv" in text:
                return "insolvency"
            if "bankrupt" in text:
                return "bankruptcy"
            if "delist" in text:
                return "delisting"
            if "suspend" in text:
                return "suspension"
            if "pledge" in text:
                return "pledge_increase"
            if "promoter" in text and "sell" in text:
                return "promoter_sell"
            if "rating" in text:
                return "rating_downgrade"
            if "order" in text:
                return "order_cancelled"
            if "guidance" in text:
                return "guidance_cut"
            return "regulatory"

        return "other"

    # ------------------------------------------------------------------
    # EVENT SCORING
    # ------------------------------------------------------------------

    def _score_event(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:

        event_type = event["type"]
        title = event["title"]
        amount = event.get("amount")
        percent = event.get("percent")

        base = 0.0

        if event_type in self.POSITIVE_TYPES:
            base = self.POSITIVE_TYPES[event_type]

        elif event_type in self.NEGATIVE_TYPES:
            base = self.NEGATIVE_TYPES[event_type]

        else:
            base = self._text_direction(title)

        time_bucket, time_factor = self._time_factor(
            event.get("date"),
            event.get("ex_date"),
            event.get("record_date"),
        )

        material = self._materiality(
            event_type,
            amount,
            percent,
            title,
        )

        material_factor = 1.0
        if material:
            material_factor = 1.25

        score = base * time_factor * material_factor

        # Avoid allowing routine calendar events to dominate.
        if event_type in {"board_approval", "other"}:
            score = self._clamp(
                score,
                -4,
                4,
            )

        hard_negative = (
            event_type in self.HARD_NEGATIVE
        )

        if hard_negative:
            score = min(
                score,
                -25,
            )

        direction = (
            "positive"
            if score > 0
            else "negative"
            if score < 0
            else "neutral"
        )

        return {
            "type": event_type,
            "title": title[:300],
            "date": self._iso(event.get("date")),
            "ex_date": self._iso(event.get("ex_date")),
            "record_date": self._iso(event.get("record_date")),
            "amount": amount,
            "percent": percent,
            "score": round(score, 2),
            "direction": direction,
            "time_bucket": time_bucket,
            "time_factor": round(time_factor, 3),
            "material": material,
            "hard_negative": hard_negative,
        }

    def _time_factor(
        self,
        event_date: Optional[date],
        ex_date: Optional[date],
        record_date: Optional[date],
    ) -> Tuple[str, float]:

        target = (
            ex_date
            or event_date
            or record_date
        )

        if target is None:
            return "unknown", 0.75

        today = date.today()
        delta = (target - today).days

        if delta < -30:
            return "historical", 0.30

        if delta < -7:
            return "recent", 0.60

        if delta <= 2:
            return "near_term", 1.50

        if delta <= 7:
            return "short_term", 1.25

        if delta <= 30:
            return "medium_term", 0.90

        if delta <= 90:
            return "future", 0.60

        return "distant", 0.35

    def _materiality(
        self,
        event_type: str,
        amount: Optional[float],
        percent: Optional[float],
        title: str,
    ) -> bool:

        if event_type in self.HARD_NEGATIVE:
            return True

        if amount is not None:
            if amount >= 100:
                return True

        if percent is not None:
            if abs(percent) >= 5:
                return True

        major_terms = (
            "multi-billion",
            "billion",
            "crore",
            "major",
            "strategic",
            "large",
            "record",
            "material",
            "landmark",
        )

        text = title.lower()

        return any(
            term in text
            for term in major_terms
        )

    def _text_direction(
        self,
        title: str,
    ) -> float:

        text = title.lower()

        positive = sum(
            1 for term in self.POSITIVE_TERMS
            if term in text
        )

        negative = sum(
            1 for term in self.NEGATIVE_TERMS
            if term in text
        )

        if positive > negative:
            return 3.0

        if negative > positive:
            return -5.0

        return 0.0

    # ------------------------------------------------------------------
    # EVENT INTERPRETATION
    # ------------------------------------------------------------------

    def _reasons(
        self,
        scored: List[Dict[str, Any]],
    ) -> List[str]:

        reasons = []

        ordered = sorted(
            scored,
            key=lambda x: abs(x["score"]),
            reverse=True,
        )

        for event in ordered:
            score = event["score"]
            title = event["title"]

            if score >= 5:
                reasons.append(
                    f"Positive corporate event: {title}"
                )

            elif score <= -5:
                reasons.append(
                    f"Negative corporate event: {title}"
                )

        near_term = [
            e for e in scored
            if e["time_bucket"] == "near_term"
            and abs(e["score"]) >= 3
        ]

        if near_term:
            reasons.append(
                "Material near-term corporate event detected"
            )

        return reasons

    def _warnings(
        self,
        scored: List[Dict[str, Any]],
    ) -> List[str]:

        warnings = []

        for event in scored:
            if event["hard_negative"]:
                warnings.append(
                    f"Hard-risk corporate event: {event['title']}"
                )

            elif event["score"] <= -8:
                warnings.append(
                    f"Material negative event: {event['title']}"
                )

        for event in scored:
            if (
                event["type"] == "promoter_sell"
                and event["time_bucket"]
                in {"near_term", "short_term"}
            ):
                warnings.append(
                    "Recent promoter selling event present"
                )

            if event["type"] == "pledge_increase":
                warnings.append(
                    "Promoter pledge increase detected"
                )

        return warnings

    def _bias(
        self,
        positive: float,
        negative: float,
    ) -> str:

        if positive > negative * 1.30:
            return "BULLISH"

        if negative > positive * 1.30:
            return "BEARISH"

        return "NEUTRAL"

    # ------------------------------------------------------------------
    # QUALITY / CONFIDENCE
    # ------------------------------------------------------------------

    def _data_quality(
        self,
        events: List[Dict[str, Any]],
    ) -> str:

        if not events:
            return "NONE"

        dated = sum(
            1 for e in events
            if e.get("date")
            or e.get("ex_date")
            or e.get("record_date")
        )

        typed = sum(
            1 for e in events
            if e.get("type") != "other"
        )

        ratio = (
            (dated / len(events))
            + (typed / len(events))
        ) / 2

        if ratio >= 0.85:
            return "HIGH"

        if ratio >= 0.55:
            return "MEDIUM"

        return "LOW"

    def _confidence(
        self,
        events: List[Dict[str, Any]],
        quality: str,
    ) -> float:

        if quality == "NONE":
            return 25.0

        base = {
            "HIGH": 72.0,
            "MEDIUM": 58.0,
            "LOW": 42.0,
        }.get(quality, 30.0)

        if events:
            base += min(
                15,
                len(events) * 1.5,
            )

        if any(
            e["material"]
            for e in events
        ):
            base += 5

        return self._clamp(
            base,
            0,
            100,
        )

    # ------------------------------------------------------------------
    # DATE / NUMBER HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _date_from(value: Any) -> Optional[date]:
        if value is None or value == "":
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        text = str(value).strip()

        formats = (
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%B %d, %Y",
        )

        for fmt in formats:
            try:
                return datetime.strptime(
                    text,
                    fmt,
                ).date()
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(
                text.replace("Z", "+00:00")
            ).date()
        except Exception:
            return None

    def _event_date(
        self,
        row: Mapping[str, Any],
    ) -> Optional[date]:

        for key in (
            "date",
            "event_date",
            "announcement_date",
            "effective_date",
            "meeting_date",
            "trade_date",
        ):
            parsed = self._date_from(
                row.get(key)
            )
            if parsed:
                return parsed

        return None

    @staticmethod
    def _number(value: Any) -> Optional[float]:
        if value is None or value == "":
            return None

        try:
            if isinstance(value, str):
                cleaned = (
                    value
                    .replace(",", "")
                    .replace("%", "")
                    .replace("₹", "")
                    .strip()
                )
                value = cleaned

            number = float(value)

            if math.isfinite(number):
                return number

        except (
            TypeError,
            ValueError,
        ):
            pass

        return None

    @staticmethod
    def _iso(value: Any) -> Optional[str]:
        if value is None:
            return None

        try:
            return value.isoformat()
        except Exception:
            return str(value)

    @staticmethod
    def _fingerprint(
        event: Dict[str, Any],
    ) -> str:

        return "|".join(
            str(event.get(key) or "")
            for key in (
                "type",
                "title",
                "date",
                "ex_date",
                "record_date",
                "amount",
            )
        ).lower()

    # ------------------------------------------------------------------
    # GENERIC
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(
        value: float,
        low: float,
        high: float,
    ) -> float:
        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return low

        return max(
            low,
            min(
                high,
                value,
            ),
        )

    @staticmethod
    def _dedupe(
        values: Iterable[str],
    ) -> List[str]:

        result = []
        seen = set()

        for value in values:
            text = str(value).strip()

            if text and text not in seen:
                seen.add(text)
                result.append(text)

        return result

    @staticmethod
    def _grade(
        score: float,
    ) -> str:

        if score >= 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        if score >= 45:
            return "D"
        return "F"

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "engine": self.NAME,
            "priority": self.priority,
            "mandatory": self.mandatory,
            "coverage": [
                "Results",
                "Dividend",
                "Bonus",
                "Split",
                "Rights",
                "Buyback",
                "QIP",
                "OFS",
                "Fund Raising",
                "Merger",
                "Demerger",
                "Acquisition",
                "Divestment",
                "Promoter Activity",
                "Pledge",
                "Board Events",
                "Orders",
                "Ratings",
                "Regulatory",
                "Legal",
            ],
        }


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------

def get_corporate_action_engine(
    provider=None,
    repository=None,
) -> CorporateActionEngine:
    return CorporateActionEngine(
        provider=provider,
        repository=repository,
    )


__all__ = [
    "CorporateActionEngine",
    "get_corporate_action_engine",
]