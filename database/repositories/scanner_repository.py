"""
TrendForge
Scanner Repository
"""

from datetime import datetime

from database.database import Database


class ScannerRepository:

    def __init__(self):

        self.db = Database()

    # ==========================================
    # Save Scan Result
    # ==========================================

    def save(

        self,

        symbol,

        exchange,

        scanner,

        signal,

        score,

        price,

        volume,

        timeframe,

        reasons,

    ):

        self.db.execute(

            """

            INSERT INTO scanner_results(

                symbol,

                exchange,

                scanner,

                signal,

                score,

                price,

                volume,

                timeframe,

                reasons,

                scan_time

            )

            VALUES(

                ?,?,?,?,?,?,?,?,?,?

            )

            """,

            (

                symbol,

                exchange,

                scanner,

                signal,

                score,

                price,

                volume,

                timeframe,

                reasons,

                datetime.now(),

            ),

        )

    # ==========================================
    # Latest Signals
    # ==========================================

    def latest(

        self,

        limit=100,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM scanner_results

            ORDER BY scan_time DESC

            LIMIT ?

            """,

            (limit,),

        )

    # ==========================================
    # By Symbol
    # ==========================================

    def by_symbol(

        self,

        symbol,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM scanner_results

            WHERE symbol=?

            ORDER BY scan_time DESC

            """,

            (symbol,),

        )

    # ==========================================
    # By Scanner
    # ==========================================

    def by_scanner(

        self,

        scanner,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM scanner_results

            WHERE scanner=?

            ORDER BY scan_time DESC

            """,

            (scanner,),

        )

    # ==========================================
    # Strong Signals
    # ==========================================

    def strong_signals(

        self,

        minimum_score=80,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM scanner_results

            WHERE score>=?

            ORDER BY score DESC

            """,

            (minimum_score,),

        )

    # ==========================================
    # Delete Old Data
    # ==========================================

    def clear(self):

        self.db.execute(

            """

            DELETE FROM scanner_results

            """

        )

    # ==========================================
    # Count
    # ==========================================

    def count(self):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM scanner_results

            """

        )

        return row["total"]