def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS alerts_log(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        scanner TEXT,

        signal TEXT,

        score REAL,

        timeframe TEXT,

        alert_time DATETIME,

        discord_message_id TEXT

    )

    """)