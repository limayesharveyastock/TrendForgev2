"""
services/corporate_action_service.py
====================================

TrendForge Corporate Action Service

Responsibilities
----------------
- Fetch corporate actions from NSE
- Store actions in database
- Detect upcoming events
- Calculate corporate action score
- Cache results
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

from providers.nse_provider import nse_provider
from database.repositories.corporate_repository import CorporateRepository

logger = logging.getLogger(__name__)


class CorporateActionService:

    CACHE_TTL = 3600

    ####################################################################
    # Event Weights
    ####################################################################

    EVENT_SCORES = {

        "BONUS": 8,
        "STOCK SPLIT": 7,
        "SPLIT": 7,
        "DIVIDEND": 5,
        "BUYBACK": 9,
        "RIGHTS": 3,
        "MERGER": 8,
        "DEMERGER": 7,
        "ACQUISITION": 8,
        "BOARD MEETING": 2,
        "AGM": 1,
        "EGM": 1,
        "RESULT": 4,
        "EARNINGS": 4,
        "PREFERENTIAL ISSUE": 2,

        "PENALTY": -6,
        "DEFAULT": -8,
        "INSOLVENCY": -10,
        "DELISTING": -10,
        "DOWNGRADE": -6,
        "RESIGNATION": -3,
    }

    ####################################################################

    def __init__(self):

        self.repo = CorporateRepository()

        self.cache = {}

        self.lock = threading.Lock()

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

    ####################################################################

    def _cache_set(self, key, value):

        self.cache[key] = (
            value,
            time.time()
        )

    ####################################################################
    # Fetch
    ####################################################################

    def get_actions(
            self,
            symbol: str,
            force_refresh=False
    ) -> List[Dict]:

        symbol = symbol.upper()

        if not force_refresh:

            cached = self._cache_get(symbol)

            if cached is not None:
                return cached

        actions = []

        try:

            data = nse_provider.corporate_actions()

            for item in data:

                text = str(item).upper()

                if symbol in text:

                    action = {

                        "symbol": symbol,

                        "subject": item.get(
                            "subject",
                            ""
                        ),

                        "purpose": item.get(
                            "purpose",
                            ""
                        ),

                        "date": item.get(
                            "date",
                            ""
                        ),

                        "details": item

                    }

                    action["score"] = self.score_action(
                        action["subject"] +
                        " " +
                        action["purpose"]
                    )

                    actions.append(action)

        except Exception as e:

            logger.exception(e)

        self._cache_set(symbol, actions)

        return actions

    ####################################################################
    # Score
    ####################################################################

    def score_action(self, text: str) -> int:

        text = text.upper()

        score = 0

        for event, weight in self.EVENT_SCORES.items():

            if event in text:
                score += weight

        score = max(-10, min(score, 10))

        return score

    ####################################################################
    # Overall Score
    ####################################################################

    def calculate_action_score(
            self,
            symbol: str
    ) -> int:

        actions = self.get_actions(symbol)

        if not actions:
            return 0

        total = sum(
            a["score"]
            for a in actions
        )

        return round(total / len(actions))

    ####################################################################
    # Upcoming Events
    ####################################################################

    def upcoming_actions(
            self,
            days=30
    ) -> List[Dict]:

        result = []

        limit = datetime.today() + timedelta(days=days)

        try:

            data = nse_provider.corporate_actions()

            for item in data:

                date_str = item.get("date")

                if not date_str:
                    continue

                try:

                    event_date = datetime.strptime(
                        date_str,
                        "%d-%b-%Y"
                    )

                except Exception:

                    try:

                        event_date = datetime.strptime(
                            date_str,
                            "%Y-%m-%d"
                        )

                    except Exception:
                        continue

                if datetime.today() <= event_date <= limit:

                    result.append(item)

        except Exception:

            logger.exception(
                "Unable to fetch upcoming actions."
            )

        return result

    ####################################################################
    # Check Upcoming
    ####################################################################

    def has_upcoming_event(
            self,
            symbol,
            days=15
    ) -> bool:

        actions = self.upcoming_actions(days)

        symbol = symbol.upper()

        for item in actions:

            if symbol in str(item).upper():
                return True

        return False

    ####################################################################
    # Save
    ####################################################################

    def save_actions(
            self,
            symbol
    ):

        actions = self.get_actions(symbol)

        for action in actions:

            try:

                self.repo.insert_action(

                    symbol=symbol,

                    subject=action["subject"],

                    purpose=action["purpose"],

                    event_date=action["date"],

                    score=action["score"],

                    raw_data=str(action["details"])

                )

            except Exception:

                logger.exception(
                    "Unable to save corporate action."
                )

    ####################################################################
    # Refresh
    ####################################################################

    def refresh(
            self,
            symbols: List[str]
    ):

        logger.info("Refreshing Corporate Actions")

        for symbol in symbols:

            try:

                self.get_actions(
                    symbol,
                    force_refresh=True
                )

            except Exception:

                logger.exception(symbol)

    ####################################################################
    # Market Summary
    ####################################################################

    def market_summary(
            self,
            symbols: List[str]
    ) -> Dict:

        scores = defaultdict(int)

        total = 0

        for symbol in symbols:

            score = self.calculate_action_score(
                symbol
            )

            scores[symbol] = score

            total += score

        average = 0

        if scores:

            average = round(
                total / len(scores),
                2
            )

        return {

            "average_score": average,

            "stocks": dict(scores)

        }

    ####################################################################
    # High Impact Events
    ####################################################################

    def high_impact_events(
            self,
            symbols: List[str],
            threshold=7
    ) -> List[Dict]:

        events = []

        for symbol in symbols:

            actions = self.get_actions(symbol)

            for action in actions:

                if abs(action["score"]) >= threshold:

                    events.append(action)

        return events


corporate_action_service = CorporateActionService()