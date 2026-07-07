def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS settings(

        key TEXT PRIMARY KEY,

        value TEXT,

        updated_at DATETIME

    )

    """)