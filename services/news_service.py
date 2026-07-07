"""
services/news_service.py
========================

TrendForge News Service

Responsibilities
----------------
- Fetch news from multiple providers
- Remove duplicates
- Calculate sentiment
- Calculate news score
- Detect breaking news
- Save to repository
- Cache results
"""

from __future__ import annotations

import logging
import re
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from providers.yfinance_provider import yfinance_provider
from providers.nse_provider import nse_provider
from database.repositories.news_repository import NewsRepository

logger = logging.getLogger(__name__)


class NewsService:

    CACHE_TTL = 300

    POSITIVE_KEYWORDS = {
        "order",
        "contract",
        "approval",
        "acquisition",
        "buyback",
        "growth",
        "profit",
        "record",
        "upgrade",
        "expansion",
        "partnership",
        "wins",
        "strong",
        "bonus",
        "dividend",
        "breakout",
        "beat",
    }

    NEGATIVE_KEYWORDS = {
        "fraud",
        "penalty",
        "downgrade",
        "loss",
        "decline",
        "lawsuit",
        "default",
        "bankruptcy",
        "investigation",
        "warning",
        "fall",
        "crash",
        "weak",
        "miss",
        "fire",
        "resigns",
    }

    BREAKING_KEYWORDS = {
        "results",
        "earnings",
        "merger",
        "acquisition",
        "buyback",
        "split",
        "dividend",
        "bulk deal",
        "block deal",
        "order",
        "contract",
        "approval",
    }

    def __init__(self):

        self.repo = NewsRepository()

        self.cache = {}

        self.lock = threading.Lock()

    ##############################################################

    def _cache_get(self, key):

        if key not in self.cache:
            return None

        value, ts = self.cache[key]

        if time.time() - ts > self.CACHE_TTL:
            del self.cache[key]
            return None

        return value

    ##############################################################

    def _cache_set(self, key, value):

        self.cache[key] = (
            value,
            time.time()
        )

    ##############################################################

    def get_news(
            self,
            symbol: str,
            force_refresh=False
    ) -> List[Dict]:

        key = symbol.upper()

        if not force_refresh:

            cached = self._cache_get(key)

            if cached is not None:
                return cached

        news = []

        ##########################################################
        # Yahoo Finance
        ##########################################################

        try:

            yahoo_news = yfinance_provider.news(symbol)

            if yahoo_news:

                for item in yahoo_news:

                    news.append({
                        "title": item.get("title"),
                        "publisher": item.get("publisher"),
                        "link": item.get("link"),
                        "published": item.get("providerPublishTime"),
                        "source": "Yahoo"
                    })

        except Exception as e:

            logger.exception(e)

        ##########################################################
        # NSE Corporate Announcements
        ##########################################################

        try:

            corporate = nse_provider.corporate_actions()

            if corporate:

                for item in corporate:

                    if symbol.upper() in str(item):

                        news.append({
                            "title": item.get(
                                "subject",
                                "Corporate Announcement"
                            ),
                            "publisher": "NSE",
                            "published": item.get("date"),
                            "link": "",
                            "source": "NSE"
                        })

        except Exception as e:

            logger.exception(e)

        ##########################################################

        news = self.remove_duplicates(news)

        for item in news:

            item["sentiment"] = self.sentiment(
                item["title"]
            )

            item["score"] = self.score_news(
                item["title"]
            )

        self._cache_set(key, news)

        return news

    ##############################################################

    def remove_duplicates(
            self,
            news: List[Dict]
    ) -> List[Dict]:

        unique = {}

        for item in news:

            title = item.get(
                "title",
                ""
            ).strip().lower()

            if title not in unique:
                unique[title] = item

        return list(unique.values())

    ##############################################################

    def sentiment(self, title: str) -> str:

        score = self.score_news(title)

        if score > 1:
            return "Positive"

        if score < -1:
            return "Negative"

        return "Neutral"

    ##############################################################

    def score_news(self, text: str) -> int:

        text = text.lower()

        score = 0

        for word in self.POSITIVE_KEYWORDS:

            if word in text:
                score += 2

        for word in self.NEGATIVE_KEYWORDS:

            if word in text:
                score -= 2

        return max(-10, min(score, 10))

    ##############################################################

    def calculate_news_score(
            self,
            symbol: str
    ) -> int:

        news = self.get_news(symbol)

        if not news:
            return 0

        total = sum(
            n["score"]
            for n in news
        )

        total = total / len(news)

        return round(total)

    ##############################################################

    def has_breaking_news(
            self,
            symbol
    ) -> bool:

        news = self.get_news(symbol)

        for item in news:

            title = item["title"].lower()

            for keyword in self.BREAKING_KEYWORDS:

                if keyword in title:
                    return True

        return False

    ##############################################################

    def latest_news(
            self,
            symbols: List[str]
    ) -> Dict:

        result = {}

        for symbol in symbols:

            result[symbol] = self.get_news(symbol)

        return result

    ##############################################################

    def save_news(
            self,
            symbol: str
    ):

        news = self.get_news(symbol)

        for item in news:

            try:

                self.repo.insert_news(

                    symbol=symbol,

                    title=item["title"],

                    source=item["source"],

                    publisher=item["publisher"],

                    sentiment=item["sentiment"],

                    score=item["score"],

                    published=item["published"],

                    url=item["link"]

                )

            except Exception:

                logger.exception(
                    "Unable to save news."
                )

    ##############################################################

    def refresh(
            self,
            symbols: List[str]
    ):

        logger.info("Refreshing news...")

        for symbol in symbols:

            try:

                self.get_news(
                    symbol,
                    force_refresh=True
                )

            except Exception:

                logger.exception(symbol)

    ##############################################################

    def market_sentiment(
            self,
            symbols: List[str]
    ) -> Dict:

        scores = defaultdict(int)

        total = 0

        for symbol in symbols:

            score = self.calculate_news_score(
                symbol
            )

            scores[symbol] = score

            total += score

        avg = 0

        if scores:
            avg = round(
                total / len(scores),
                2
            )

        return {

            "average_score": avg,

            "stocks": dict(scores)

        }


news_service = NewsService()