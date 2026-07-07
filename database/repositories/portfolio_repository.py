"""
TrendForge
Portfolio Repository
"""

from datetime import datetime

from database.database import Database


class PortfolioRepository:

    def __init__(self):

        self.db = Database()

    # =====================================================
    # Save / Update Holding
    # =====================================================

    def save(
        self,
        symbol,
        quantity,
        average_price,
        ltp,
        sector=None,
        exchange="NSE",
    ):

        current_value = quantity * ltp
        investment = quantity * average_price
        pnl = current_value - investment

        self.db.execute(
            """
            INSERT OR REPLACE INTO portfolio(

                symbol,
                exchange,
                sector,
                quantity,
                average_price,
                ltp,
                investment,
                current_value,
                pnl,
                updated_at

            )

            VALUES(?,?,?,?,?,?,?,?,?,?)

            """,
            (
                symbol,
                exchange,
                sector,
                quantity,
                average_price,
                ltp,
                investment,
                current_value,
                pnl,
                datetime.now(),
            ),
        )

    # =====================================================
    # Save Multiple Holdings
    # =====================================================

    def save_many(self, holdings):

        for holding in holdings:

            self.save(
                symbol=holding["symbol"],
                quantity=holding["quantity"],
                average_price=holding["average_price"],
                ltp=holding["ltp"],
                sector=holding.get("sector"),
                exchange=holding.get("exchange", "NSE"),
            )

    # =====================================================
    # Get Holding
    # =====================================================

    def get(self, symbol):

        return self.db.fetchone(
            """
            SELECT *

            FROM portfolio

            WHERE symbol=?
            """,
            (symbol,),
        )

    # =====================================================
    # All Holdings
    # =====================================================

    def all(self):

        return self.db.fetchall(
            """
            SELECT *

            FROM portfolio

            ORDER BY current_value DESC
            """
        )

    # =====================================================
    # Portfolio Value
    # =====================================================

    def portfolio_value(self):

        row = self.db.fetchone(
            """
            SELECT SUM(current_value) total

            FROM portfolio
            """
        )

        return row["total"] or 0

    # =====================================================
    # Total Investment
    # =====================================================

    def investment(self):

        row = self.db.fetchone(
            """
            SELECT SUM(investment) total

            FROM portfolio
            """
        )

        return row["total"] or 0

    # =====================================================
    # Total P&L
    # =====================================================

    def total_pnl(self):

        row = self.db.fetchone(
            """
            SELECT SUM(pnl) total

            FROM portfolio
            """
        )

        return row["total"] or 0

    # =====================================================
    # Sector Allocation
    # =====================================================

    def sector_allocation(self):

        return self.db.fetchall(
            """
            SELECT

                sector,

                SUM(current_value) value

            FROM portfolio

            GROUP BY sector

            ORDER BY value DESC
            """
        )

    # =====================================================
    # Top Gainers
    # =====================================================

    def top_gainers(self, limit=10):

        return self.db.fetchall(
            """
            SELECT *

            FROM portfolio

            ORDER BY pnl DESC

            LIMIT ?
            """,
            (limit,),
        )

    # =====================================================
    # Top Losers
    # =====================================================

    def top_losers(self, limit=10):

        return self.db.fetchall(
            """
            SELECT *

            FROM portfolio

            ORDER BY pnl ASC

            LIMIT ?
            """,
            (limit,),
        )

    # =====================================================
    # Remove Holding
    # =====================================================

    def remove(self, symbol):

        self.db.execute(
            """
            DELETE FROM portfolio

            WHERE symbol=?
            """,
            (symbol,),
        )

    # =====================================================
    # Clear Portfolio
    # =====================================================

    def clear(self):

        self.db.execute(
            """
            DELETE FROM portfolio
            """
        )

    # =====================================================
    # Count
    # =====================================================

    def count(self):

        row = self.db.fetchone(
            """
            SELECT COUNT(*) total

            FROM portfolio
            """
        )

        return row["total"]