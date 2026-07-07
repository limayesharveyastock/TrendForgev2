def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS instruments(

        instrument_token INTEGER PRIMARY KEY,

        exchange_token INTEGER,

        tradingsymbol TEXT,

        name TEXT,

        last_price REAL,

        expiry TEXT,

        strike REAL,

        tick_size REAL,

        lot_size INTEGER,

        instrument_type TEXT,

        segment TEXT,

        exchange TEXT

    )

    """)