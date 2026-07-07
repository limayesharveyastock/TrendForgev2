"""
TrendForge
Option Chain Migration
"""


def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS option_chain(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT NOT NULL,

        expiry DATE NOT NULL,

        strike REAL NOT NULL,

        option_type TEXT NOT NULL,

        ltp REAL,

        bid REAL,

        ask REAL,

        volume INTEGER,

        oi INTEGER,

        oi_change INTEGER,

        iv REAL,

        delta REAL,

        gamma REAL,

        theta REAL,

        vega REAL,

        rho REAL,

        intrinsic_value REAL,

        time_value REAL,

        updated_at DATETIME,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # --------------------------------------------------
    # Indexes
    # --------------------------------------------------

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_option_symbol

    ON option_chain(symbol)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_option_expiry

    ON option_chain(expiry)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_option_strike

    ON option_chain(strike)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_option_type

    ON option_chain(option_type)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_option_symbol_expiry

    ON option_chain(symbol, expiry)

    """)