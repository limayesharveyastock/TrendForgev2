"""
TrendForge v2
HTTP Client

Shared HTTP client for all
fundamental providers.
"""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15
RATE_LIMIT_DELAY = 0.50
CACHE_DIR = Path("cache/http")

CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
]


class HTTPClient:
    """
    Shared HTTP client.

    Features
    --------
    • Retry
    • Session reuse
    • Timeout
    • Random User-Agent
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        ) -> None:

        self.timeout = timeout
        self.request_count = 0
        self.failed_requests = 0
        self.total_time = 0.0
        self.last_request = None

        self.session = requests.Session()

        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
        )

        adapter = HTTPAdapter(
            max_retries=retries,
        )

        self.session.mount(
            "https://",
            adapter,
        )

        self.session.mount(
            "http://",
            adapter,
        )

        logger.info(
            "HTTP Client initialized."
        )

    # --------------------------------------------------

    def headers(self) -> Dict[str, str]:

        return {
            "User-Agent": random.choice(
                USER_AGENTS
            ),
            "Accept": "application/json,text/html",
            "Connection": "keep-alive",
        }

    # --------------------------------------------------

    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
    ) -> requests.Response:

        start = time.time()

        logger.info(
         "GET %s",
         url,
        )

time.sleep(RATE_LIMIT_DELAY)

        response = self.session.get(
            url,
            params=params,
            headers=self.headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()try:

    response.raise_for_status()

except Exception:

    self.failed_requests += 1

    logger.exception(
        "HTTP request failed."
    )

    raise

        self.request_count += 1

        self.last_request = datetime.now()

        self.total_time += (
        time.time() - start
        )

return response

    # --------------------------------------------------

    def post(
        self,
        url: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> requests.Response:

        logger.info(
            "POST %s",
            url,
        )
        start = time.time()

        ime.sleep(RATE_LIMIT_DELAY)
        response = self.session.post(
            url,
            json=json,
            data=data,
            headers=self.headers(),
            timeout=self.timeout,
        )

        try:

        response.raise_for_status()

        except Exception:

        self.failed_requests += 1

        logger.exception(
        "HTTP request failed."
        )

    raise

        self.request_count += 1

        self.last_request = datetime.now()

        self.total_time += (
        time.time() - start
        )

return response

    # --------------------------------------------------

    def get_json(
        self,
        url: str,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:

        return self.get(
            url,
            params=params,
        ).json()

    # --------------------------------------------------

    def get_text(
        self,
        url: str,
    ) -> str:

        return self.get(
            url,
        ).text
        def health(self):

    return {

        "requests": self.request_count,

        "failed": self.failed_requests,

        "average_time":
        round(
            self.total_time /
            max(self.request_count, 1),
            3,
        ),

        "last_request":
        self.last_request,

    }
    def reset_metrics(self):

    self.request_count = 0

    self.failed_requests = 0

    self.total_time = 0.0

    self.last_request = None