"""
scanner/watchlist_manager.py
============================

TrendForge Watchlist Manager

Responsibilities
----------------
- Manage multiple watchlists
- Add / Remove stocks
- Sync with database
- Import / Export watchlists
- Auto-refresh quotes
- Scanner integration
"""

from __future__ import annotations

import csv
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

from database.repositories.watchlist_repository import WatchlistRepository
from providers.kite_provider import kite_provider

logger = logging.getLogger(__name__)


class WatchlistManager:

    DEFAULT_WATCHLIST = "Default"

    def __init__(self):

        self.repo = WatchlistRepository()

        self.lock = threading.Lock()

        self.watchlists: Dict[str, List[str]] = {}

        self.load()

    ####################################################################
    # Load / Save
    ####################################################################

    def load(self):

        try:

            data = self.repo.get_all_watchlists()

            self.watchlists = {}

            for row in data:

                name = row["watchlist"]

                symbol = row["symbol"].upper()

                self.watchlists.setdefault(name, [])

                if symbol not in self.watchlists[name]:
                    self.watchlists[name].append(symbol)

            logger.info(
                "Loaded %d watchlists",
                len(self.watchlists)
            )

        except Exception:

            logger.exception(
                "Unable to load watchlists."
            )

    ####################################################################

    def refresh(self):

        self.load()

    ####################################################################
    # Watchlist CRUD
    ####################################################################

    def create_watchlist(self, name: str):

        if name not in self.watchlists:

            self.watchlists[name] = []

            logger.info("Created watchlist %s", name)

    ####################################################################

    def delete_watchlist(self, name: str):

        if name == self.DEFAULT_WATCHLIST:
            raise ValueError(
                "Default watchlist cannot be deleted."
            )

        if name in self.watchlists:

            self.repo.delete_watchlist(name)

            del self.watchlists[name]

    ####################################################################
    # Stock Operations
    ####################################################################

    def add_stock(
            self,
            symbol: str,
            watchlist: str = DEFAULT_WATCHLIST
    ):

        symbol = symbol.upper()

        self.watchlists.setdefault(watchlist, [])

        if symbol in self.watchlists[watchlist]:
            return

        self.watchlists[watchlist].append(symbol)

        self.repo.add_stock(
            watchlist,
            symbol
        )

    ####################################################################

    def remove_stock(
            self,
            symbol: str,
            watchlist: str = DEFAULT_WATCHLIST
    ):

        symbol = symbol.upper()

        if watchlist not in self.watchlists:
            return

        if symbol not in self.watchlists[watchlist]:
            return

        self.watchlists[watchlist].remove(symbol)

        self.repo.remove_stock(
            watchlist,
            symbol
        )

    ####################################################################
    # Queries
    ####################################################################

    def get_watchlist(
            self,
            name=DEFAULT_WATCHLIST
    ) -> List[str]:

        return sorted(
            self.watchlists.get(name, [])
        )

    ####################################################################

    def all_watchlists(self):

        return self.watchlists

    ####################################################################

    def all_symbols(self):

        symbols = set()

        for stocks in self.watchlists.values():

            symbols.update(stocks)

        return sorted(symbols)

    ####################################################################
    # Quotes
    ####################################################################

    def quotes(
            self,
            watchlist=DEFAULT_WATCHLIST
    ):

        symbols = self.get_watchlist(watchlist)

        if not symbols:
            return {}

        instruments = [
            f"NSE:{s}"
            for s in symbols
        ]

        try:

            return kite_provider.safe_quote(
                instruments
            )

        except Exception:

            logger.exception(
                "Unable to fetch quotes."
            )

            return {}

    ####################################################################
    # Scanner
    ####################################################################

    def scanner_symbols(self):

        return self.all_symbols()

    ####################################################################
    # Import / Export
    ####################################################################

    def export_csv(
            self,
            path,
            watchlist=DEFAULT_WATCHLIST
    ):

        with open(path, "w", newline="") as f:

            writer = csv.writer(f)

            writer.writerow(["Symbol"])

            for stock in self.get_watchlist(
                    watchlist
            ):
                writer.writerow([stock])

    ####################################################################

    def import_csv(
            self,
            path,
            watchlist=DEFAULT_WATCHLIST
    ):

        with open(path) as f:

            reader = csv.DictReader(f)

            for row in reader:

                self.add_stock(
                    row["Symbol"],
                    watchlist
                )

    ####################################################################

    def export_json(self, path):

        with open(path, "w") as f:

            json.dump(
                self.watchlists,
                f,
                indent=4
            )

    ####################################################################

    def import_json(self, path):

        with open(path) as f:

            data = json.load(f)

        for watchlist, stocks in data.items():

            for stock in stocks:

                self.add_stock(
                    stock,
                    watchlist
                )

    ####################################################################
    # Validation
    ####################################################################

    def exists(
            self,
            symbol,
            watchlist=DEFAULT_WATCHLIST
    ):

        return symbol.upper() in self.watchlists.get(
            watchlist,
            []
        )

    ####################################################################

    def count(
            self,
            watchlist=DEFAULT_WATCHLIST
    ):

        return len(
            self.watchlists.get(
                watchlist,
                []
            )
        )

    ####################################################################
    # Utilities
    ####################################################################

    def clear(
            self,
            watchlist=DEFAULT_WATCHLIST
    ):

        for stock in list(
                self.watchlists.get(
                    watchlist,
                    []
                )):

            self.remove_stock(
                stock,
                watchlist
            )

    ####################################################################

    def statistics(self):

        return {
            "watchlists": len(self.watchlists),
            "total_symbols": len(self.all_symbols()),
            "details": {
                name: len(symbols)
                for name, symbols in self.watchlists.items()
            }
        }


watchlist_manager = WatchlistManager()