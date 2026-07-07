"""
TrendForge
Corporate Actions Repository
"""

from datetime import datetime

from database.database import Database


class CorporateRepository:

    def __init__(self):

        self.db = Database()

    # =====================================================
    # Save Corporate Action
    # =====================================================

    def save(

        self,

        symbol,

        action_type,

        announcement_date,

        record_date,

        remarks="",

    ):

        self.db.execute(

            """

            INSERT INTO corporate_actions(

                symbol,

                action_type,

                announcement_date,

                record_date,

                remarks

            )

            VALUES(?,?,?,?,?)

            """,

            (

                symbol,

                action_type,

                announcement_date,

                record_date,

                remarks,

            ),

        )

    # =====================================================
    # Save Multiple Actions
    # =====================================================

    def save_many(

        self,

        actions,

    ):

        rows = []

        for action in actions:

            rows.append(

                (

                    action["symbol"],

                    action["action_type"],

                    action["announcement_date"],

                    action["record_date"],

                    action.get("remarks", ""),

                )

            )

        self.db.executemany(

            """

            INSERT INTO corporate_actions(

                symbol,

                action_type,

                announcement_date,

                record_date,

                remarks

            )

            VALUES(?,?,?,?,?)

            """,

            rows,

        )

    # =====================================================
    # By Symbol
    # =====================================================

    def by_symbol(

        self,

        symbol,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM corporate_actions

            WHERE symbol=?

            ORDER BY announcement_date DESC

            """,

            (symbol,),

        )

    # =====================================================
    # Upcoming Actions
    # =====================================================

    def upcoming(self):

        today = datetime.now().date()

        return self.db.fetchall(

            """

            SELECT *

            FROM corporate_actions

            WHERE record_date>=?

            ORDER BY record_date

            """,

            (today,),

        )

    # =====================================================
    # By Action Type
    # =====================================================

    def by_action(

        self,

        action_type,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM corporate_actions

            WHERE action_type=?

            ORDER BY announcement_date DESC

            """,

            (action_type,),

        )

    # =====================================================
    # Latest
    # =====================================================

    def latest(

        self,

        limit=100,

    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM corporate_actions

            ORDER BY announcement_date DESC

            LIMIT ?

            """,

            (limit,),

        )

    # =====================================================
    # Delete Symbol
    # =====================================================

    def delete_symbol(

        self,

        symbol,

    ):

        self.db.execute(

            """

            DELETE FROM corporate_actions

            WHERE symbol=?

            """,

            (symbol,),

        )

    # =====================================================
    # Delete All
    # =====================================================

    def clear(self):

        self.db.execute(

            """

            DELETE FROM corporate_actions

            """

        )

    # =====================================================
    # Count
    # =====================================================

    def count(self):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM corporate_actions

            """

        )

        return row["total"]

    # =====================================================
    # Exists
    # =====================================================

    def exists(

        self,

        symbol,

        action_type,

        record_date,

    ):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM corporate_actions

            WHERE symbol=?

            AND action_type=?

            AND record_date=?

            """,

            (

                symbol,

                action_type,

                record_date,

            ),

        )

        return row["total"] > 0