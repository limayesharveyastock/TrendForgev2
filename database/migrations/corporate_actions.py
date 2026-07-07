def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS corporate_actions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        action_type TEXT,

        announcement_date DATE,

        record_date DATE,

        remarks TEXT

    )

    """)
