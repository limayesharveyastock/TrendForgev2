def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS trade_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        side TEXT,

        quantity INTEGER,

        entry_price REAL,

        exit_price REAL,

        stoploss REAL,

        target REAL,

        pnl REAL,

        status TEXT,

        broker_order_id TEXT,

        created_at DATETIME

    )

    """)