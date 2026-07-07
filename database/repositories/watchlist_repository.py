"""
TrendForge
Watchlist Repository
"""

from datetime import datetime

from database.database import Database


class WatchlistRepository:

    def __init__(self):

        self.db = Database()

    # =====================================================
    # Add Stock
    # =====================================================

    def add(
    self,
    watchlist,
    symbol,
    exchange="NSE",
    notes="",
    priority=1,
    target=None,
    stoploss=None,
    scanner=None,
    score=None,
    last_signal=None,
):

        self.db.execute(

            """

            INSERT INTO watchlists(

                watchlist,

                symbol,

                exchange,

                notes,

                priority,

                created_at

            )

            VALUES(?,?,?,?,?,?)

            """,

            (

                watchlist,

                symbol,

                exchange,

                notes,

                priority,

                datetime.now(),

            ),

        )

    # =====================================================
    # Update Stock
    # =====================================================

    def update(

        self,

        watchlist,

        symbol,

        notes=None,

        priority=None,

    ):

        fields = []
        values = []

        if notes is not None:
            fields.append("notes=?")
            values.append(notes)

        if priority is not None:
            fields.append("priority=?")
            values.append(priority)

        if not fields:
            return

        values.extend([watchlist, symbol])

        self.db.execute(

            f"""

            UPDATE watchlists

            SET {', '.join(fields)}

            WHERE watchlist=?

            AND symbol=?

            """,

            tuple(values),

        )

    # =====================================================
    # Remove Stock
    # =====================================================

    def remove(

        self,

        watchlist,

        symbol,

    ):

        self.db.execute(

            """

            DELETE FROM watchlists

            WHERE watchlist=?

            AND symbol=?

            """,

            (

                watchlist,

                symbol,

            ),

        )

    # =====================================================
    # Get Watchlist
    # =====================================================

    def get(

        self,

        watchlist,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM watchlists

            WHERE watchlist=?

            ORDER BY priority DESC,
                     symbol

            """,

            (watchlist,),

        )

    # =====================================================
    # Get All Watchlists
    # =====================================================

    def watchlists(self):

        rows = self.db.fetchall(

            """

            SELECT DISTINCT watchlist

            FROM watchlists

            ORDER BY watchlist

            """

        )

        return [

            row["watchlist"]

            for row in rows

        ]

    # =====================================================
    # Exists
    # =====================================================

    def exists(

        self,

        watchlist,

        symbol,

    ):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM watchlists

            WHERE watchlist=?

            AND symbol=?

            """,

            (

                watchlist,

                symbol,

            ),

        )

        return row["total"] > 0

    # =====================================================
    # Symbols Only
    # =====================================================

    def symbols(

        self,

        watchlist,

    ):

        rows = self.db.fetchall(

            """

            SELECT symbol

            FROM watchlists

            WHERE watchlist=?

            ORDER BY priority DESC

            """,

            (watchlist,),

        )

        return [

            row["symbol"]

            for row in rows

        ]

    # =====================================================
    # Delete Watchlist
    # =====================================================

    def delete_watchlist(

        self,

        watchlist,

    ):

        self.db.execute(

            """

            DELETE FROM watchlists

            WHERE watchlist=?

            """,

            (watchlist,),

        )

    # =====================================================
    # Clear All
    # =====================================================

    def clear(self):

        self.db.execute(

            """

            DELETE FROM watchlists

            """

        )

    # =====================================================
    # Count
    # =====================================================

    def count(self):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM watchlists

            """

        )

        return row["total"]