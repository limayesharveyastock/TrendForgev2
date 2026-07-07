def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS scanner_results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        exchange TEXT,

        scanner TEXT,

        signal TEXT,

        score REAL,

        price REAL,

        volume INTEGER,

        timeframe TEXT,

        reasons TEXT,

        scan_time DATETIME

    )

    """)
