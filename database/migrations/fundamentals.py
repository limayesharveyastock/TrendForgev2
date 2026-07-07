def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS fundamentals(

        symbol TEXT PRIMARY KEY,

        market_cap REAL,

        pe REAL,
        pb REAL,
        eps REAL,

        roe REAL,
        roce REAL,

        debt_to_equity REAL,

        sales_growth REAL,
        profit_growth REAL,

        promoter_holding REAL,
        fii_holding REAL,
        dii_holding REAL,

        dividend_yield REAL,

        current_ratio REAL,
        quick_ratio REAL,

        book_value REAL,
        face_value REAL,

        sector TEXT,
        industry TEXT,

        updated_at DATETIME

    )

    """)
    