"""
TrendForge
News Migration
"""


def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS news(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT NOT NULL,

        exchange TEXT DEFAULT 'NSE',

        headline TEXT NOT NULL,

        summary TEXT,

        source TEXT,

        url TEXT,

        category TEXT,

        sentiment REAL DEFAULT 0,

        impact_score REAL DEFAULT 0,

        published_at DATETIME,

        fetched_at DATETIME,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # -----------------------------------------------------
    # Indexes
    # -----------------------------------------------------

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_news_symbol

    ON news(symbol)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_news_published

    ON news(published_at)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_news_sentiment

    ON news(sentiment)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_news_category

    ON news(category)

    """)

    db.execute("""

    CREATE INDEX IF NOT EXISTS idx_news_source

    ON news(source)

    """)