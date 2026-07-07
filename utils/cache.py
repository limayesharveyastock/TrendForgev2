"""
utils/cache.py
==============

Centralized in-memory cache for TrendForge.

Features
--------
✓ Thread-safe
✓ TTL (Time-To-Live)
✓ Automatic expiration
✓ LRU eviction
✓ Cache statistics
✓ Decorator support
✓ Manual invalidation
✓ Pattern deletion
✓ Singleton instance

Used by
-------
- scanner_engine
- kite_provider
- nse_provider
- yfinance_provider
- news_service
- corporate_action_service
- ai_engine
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Optional


class Cache:

    def __init__(
        self,
        max_size: int = 5000,
        default_ttl: int = 300
    ):

        self.max_size = max_size
        self.default_ttl = default_ttl

        self.cache = OrderedDict()

        self.lock = threading.RLock()

        self.hits = 0
        self.misses = 0
        self.evictions = 0

    ##################################################################
    # Internal
    ##################################################################

    def _expired(self, expiry):

        return expiry is not None and expiry < time.time()

    ##################################################################
    # CRUD
    ##################################################################

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):

        ttl = ttl if ttl is not None else self.default_ttl

        expiry = None

        if ttl > 0:
            expiry = time.time() + ttl

        with self.lock:

            if key in self.cache:
                del self.cache[key]

            elif len(self.cache) >= self.max_size:

                self.cache.popitem(last=False)
                self.evictions += 1

            self.cache[key] = (value, expiry)

    ##################################################################

    def get(
        self,
        key: str,
        default=None
    ):

        with self.lock:

            item = self.cache.get(key)

            if item is None:

                self.misses += 1
                return default

            value, expiry = item

            if self._expired(expiry):

                del self.cache[key]

                self.misses += 1

                return default

            self.cache.move_to_end(key)

            self.hits += 1

            return value

    ##################################################################

    def delete(self, key):

        with self.lock:

            self.cache.pop(key, None)

    ##################################################################

    def clear(self):

        with self.lock:

            self.cache.clear()

    ##################################################################

    def exists(self, key):

        return self.get(key) is not None

    ##################################################################
    # Pattern Delete
    ##################################################################

    def delete_pattern(self, pattern: str):

        with self.lock:

            keys = [
                key
                for key in self.cache
                if pattern in key
            ]

            for key in keys:
                del self.cache[key]

    ##################################################################
    # Cleanup
    ##################################################################

    def cleanup(self):

        with self.lock:

            expired = []

            for key, (_, expiry) in self.cache.items():

                if self._expired(expiry):
                    expired.append(key)

            for key in expired:
                del self.cache[key]

    ##################################################################
    # Statistics
    ##################################################################

    def stats(self):

        requests = self.hits + self.misses

        ratio = 0

        if requests:

            ratio = round(
                (self.hits / requests) * 100,
                2
            )

        return {

            "entries": len(self.cache),

            "hits": self.hits,

            "misses": self.misses,

            "hit_ratio": ratio,

            "evictions": self.evictions,

            "max_size": self.max_size

        }

    ##################################################################
    # Memoization Decorator
    ##################################################################

    def memoize(
        self,
        ttl: Optional[int] = None,
        key_builder: Optional[Callable] = None
    ):

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):

                if key_builder:

                    cache_key = key_builder(
                        *args,
                        **kwargs
                    )

                else:

                    cache_key = (
                        f"{func.__module__}:"
                        f"{func.__name__}:"
                        f"{args}:"
                        f"{sorted(kwargs.items())}"
                    )

                cached = self.get(cache_key)

                if cached is not None:
                    return cached

                result = func(*args, **kwargs)

                self.set(
                    cache_key,
                    result,
                    ttl
                )

                return result

            return wrapper

        return decorator

    ##################################################################
    # Convenience
    ##################################################################

    def increment(
        self,
        key,
        amount=1
    ):

        value = self.get(key, 0)

        value += amount

        self.set(key, value)

        return value

    ##################################################################

    def append(
        self,
        key,
        value
    ):

        values = self.get(key, [])

        values.append(value)

        self.set(key, values)

        return values

    ##################################################################

    def keys(self):

        with self.lock:
            return list(self.cache.keys())

    ##################################################################

    def values(self):

        with self.lock:

            return [
                value
                for value, _
                in self.cache.values()
            ]

    ##################################################################

    def size(self):

        return len(self.cache)


######################################################################
# Global Cache Instance
######################################################################

cache = Cache()