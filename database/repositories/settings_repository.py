"""
TrendForge
Settings Repository
"""

from datetime import datetime

from database.database import Database


class SettingsRepository:

    def __init__(self):

        self.db = Database()

    # =====================================================
    # Set Setting
    # =====================================================

    def set(

        self,

        key,

        value,

    ):

        self.db.execute(

            """

            INSERT OR REPLACE INTO settings(

                key,

                value,

                updated_at

            )

            VALUES(?,?,?)

            """,

            (

                key,

                str(value),

                datetime.now(),

            ),

        )

    # =====================================================
    # Get Setting
    # =====================================================

    def get(

        self,

        key,

        default=None,

    ):

        row = self.db.fetchone(

            """

            SELECT value

            FROM settings

            WHERE key=?

            """,

            (key,),

        )

        if row:

            return row["value"]

        return default

    # =====================================================
    # Get All Settings
    # =====================================================

    def all(self):

        return self.db.fetchall(

            """

            SELECT *

            FROM settings

            ORDER BY key

            """

        )

    # =====================================================
    # Check Exists
    # =====================================================

    def exists(

        self,

        key,

    ):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM settings

            WHERE key=?

            """,

            (key,),

        )

        return row["total"] > 0

    # =====================================================
    # Delete Setting
    # =====================================================

    def delete(

        self,

        key,

    ):

        self.db.execute(

            """

            DELETE FROM settings

            WHERE key=?

            """,

            (key,),

        )

    # =====================================================
    # Clear All Settings
    # =====================================================

    def clear(self):

        self.db.execute(

            """

            DELETE FROM settings

            """

        )

    # =====================================================
    # Count
    # =====================================================

    def count(self):

        row = self.db.fetchone(

            """

            SELECT COUNT(*) total

            FROM settings

            """

        )

        return row["total"]

    # =====================================================
    # Load Default Settings
    # =====================================================

    def load_defaults(self):

        defaults = {

            # Scanner
            "scanner_interval": "300",
            "default_timeframe": "15minute",
            "minimum_score": "70",

            # Risk Management
            "risk_per_trade": "1",
            "max_open_positions": "10",
            "capital": "100000",

            # Alerts
            "discord_enabled": "true",
            "alert_cooldown": "15",

            # Data
            "fundamental_provider": "tijori",
            "cache_expiry_hours": "24",

            # UI
            "theme": "dark",
            "default_watchlist": "Swing",

            # Auto Trading
            "auto_trade": "false",
            "paper_trading": "true"

        }

        for key, value in defaults.items():

            if not self.exists(key):

                self.set(key, value)