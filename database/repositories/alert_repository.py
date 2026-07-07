"""
TrendForge
Alert Repository
"""

from datetime import datetime, timedelta

from database.database import Database


class AlertRepository:

    def __init__(self):

        self.db = Database()

    # =====================================================
    # Save Alert
    # =====================================================

    def save(

        self,

        symbol,

        scanner,

        signal,

        score,

        timeframe,

        message_id=None,

    ):

        self.db.execute(

            """

            INSERT INTO alerts_log(

                symbol,

                scanner,

                signal,

                score,

                timeframe,

                alert_time,

                discord_message_id

            )

            VALUES(?,?,?,?,?,?,?)

            """,

            (

                symbol,

                scanner,

                signal,

                score,

                timeframe,

                datetime.now(),

                message_id,

            ),

        )

    # =====================================================
    # Latest Alerts
    # =====================================================

    def latest(

        self,

        limit=100,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM alerts_log

            ORDER BY alert_time DESC

            LIMIT ?

            """,

            (limit,),

        )

    # =====================================================
    # Symbol History
    # =====================================================

    def by_symbol(

        self,

        symbol,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM alerts_log

            WHERE symbol=?

            ORDER BY alert_time DESC

            """,

            (symbol,),

        )

    # =====================================================
    # Duplicate Check
    # =====================================================

    def recently_sent(

        self,

        symbol,

        scanner,

        signal,

        timeframe,

        cooldown_minutes=15,

    ):

        cutoff = datetime.now() - timedelta(
            minutes=cooldown_minutes
        )

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM alerts_log

            WHERE symbol=?

            AND scanner=?

            AND signal=?

            AND timeframe=?

            AND alert_time>=?

            """,

            (

                symbol,

                scanner,

                signal,

                timeframe,

                cutoff,

            ),

        )

        return row["total"] > 0

    # =====================================================
    # Delete Old Alerts
    # =====================================================

    def delete_older_than(

        self,

        days=30,

    ):

        cutoff = datetime.now() - timedelta(
            days=days
        )

        self.db.execute(

            """

            DELETE FROM alerts_log

            WHERE alert_time < ?

            """,

            (cutoff,),

        )

    # =====================================================
    # Clear
    # =====================================================

    def clear(self):

        self.db.execute(

            """

            DELETE FROM alerts_log

            """

        )

    # =====================================================
    # Count
    # =====================================================

    def count(self):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM alerts_log

            """

        )

        return row["total"]