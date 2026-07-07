"""
TrendForge
Fundamentals Repository
"""

from datetime import datetime

from database.database import Database


class FundamentalsRepository:

    def __init__(self):

        self.db = Database()

    # =====================================================
    # Save / Update Fundamentals
    # =====================================================

    def save(self, data):

        self.db.execute(
            """
            INSERT OR REPLACE INTO fundamentals (

                symbol,

                market_cap,
                pe,
                pb,
                eps,

                roe,
                roce,

                debt_to_equity,

                sales_growth,
                profit_growth,

                promoter_holding,
                fii_holding,
                dii_holding,

                dividend_yield,

                current_ratio,
                quick_ratio,

                book_value,

                face_value,

                sector,
                industry,

                updated_at

            )

            VALUES(

                ?,?,?,?,?,?,
                ?,?,?,?,
                ?,?,?,?,
                ?,?,?,?,
                ?,?,?

            )
            """,

            (

                data["symbol"],

                data.get("market_cap"),

                data.get("pe"),

                data.get("pb"),

                data.get("eps"),

                data.get("roe"),

                data.get("roce"),

                data.get("debt_to_equity"),

                data.get("sales_growth"),

                data.get("profit_growth"),

                data.get("promoter_holding"),

                data.get("fii_holding"),

                data.get("dii_holding"),

                data.get("dividend_yield"),

                data.get("current_ratio"),

                data.get("quick_ratio"),

                data.get("book_value"),

                data.get("face_value"),

                data.get("sector"),

                data.get("industry"),

                datetime.now().isoformat(),

            ),

        )

    # =====================================================
    # By Symbol
    # =====================================================

    def by_symbol(
        self,
        symbol,
    ):

        return self.db.fetchone(

            """

            SELECT *

            FROM fundamentals

            WHERE symbol=?

            """,

            (symbol,),

        )

    # =====================================================
    # Exists
    # =====================================================

    def exists(
        self,
        symbol,
    ):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM fundamentals

            WHERE symbol=?

            """,

            (symbol,),

        )

        return row["total"] > 0

    # =====================================================
    # Update Timestamp
    # =====================================================

    def touch(
        self,
        symbol,
    ):

        self.db.execute(

            """

            UPDATE fundamentals

            SET updated_at=?

            WHERE symbol=?

            """,

            (

                datetime.now().isoformat(),

                symbol,

            ),

        )

    # =====================================================
    # Delete Symbol
    # =====================================================

    def delete(
        self,
        symbol,
    ):

        self.db.execute(

            """

            DELETE FROM fundamentals

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

            DELETE FROM fundamentals

            """

        )

    # =====================================================
    # Latest Updated
    # =====================================================

    def latest(
        self,
        limit=100,
    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM fundamentals

            ORDER BY updated_at DESC

            LIMIT ?

            """,

            (limit,),

        )

    # =====================================================
    # Count
    # =====================================================

    def count(self):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM fundamentals

            """

        )

        return row["total"]

    # =====================================================
    # Stocks Matching PE
    # =====================================================

    def pe_less_than(
        self,
        value,
    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM fundamentals

            WHERE pe<=?

            ORDER BY pe

            """,

            (value,),

        )

    # =====================================================
    # Stocks Matching ROE
    # =====================================================

    def roe_greater_than(
        self,
        value,
    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM fundamentals

            WHERE roe>=?

            ORDER BY roe DESC

            """,

            (value,),

        )

    # =====================================================
    # Stocks Matching ROCE
    # =====================================================

    def roce_greater_than(
        self,
        value,
    ):

        return self.db.fetchall(

            """

            SELECT *

            FROM fundamentals

            WHERE roce>=?

            ORDER BY roce DESC

            """,

            (value,),

        )