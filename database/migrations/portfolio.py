def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS portfolio(

        symbol TEXT PRIMARY KEY,

        exchange TEXT,

        sector TEXT,

        quantity INTEGER,

        average_price REAL,

        ltp REAL,

        investment REAL,

        current_value REAL,

        pnl REAL,

        updated_at DATETIME

    )

    """)