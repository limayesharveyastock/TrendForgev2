"""
TrendForge
Database Migrations
"""

from database.database import Database


def create_tables():

    db = Database()

    # =====================================================
    # Instruments
    # =====================================================

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

    # =====================================================
    # Fundamentals
    # =====================================================

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

    # =====================================================
    # Corporate Actions
    # =====================================================

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

    # =====================================================
    # Scanner Results
    # =====================================================

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

    # =====================================================
    # Watchlists
    # =====================================================

    db.execute("""

    CREATE TABLE IF NOT EXISTS watchlists(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        watchlist TEXT,

        symbol TEXT,

        exchange TEXT,

        notes TEXT,

        priority INTEGER DEFAULT 1,

        target REAL,

        stoploss REAL,

        scanner TEXT,

        score REAL,

        last_signal TEXT,

        last_scan DATETIME,

        created_at DATETIME

    )

    """)

    # =====================================================
    # Alerts
    # =====================================================

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

    # =====================================================
    # Trade History
    # =====================================================

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

    # =====================================================
    # Portfolio
    # =====================================================

    db.execute("""

    CREATE TABLE IF NOT EXISTS portfolio(

        symbol TEXT PRIMARY KEY,

        quantity INTEGER,

        average_price REAL,

        ltp REAL,

        current_value REAL,

        pnl REAL,

        updated_at DATETIME

    )

    """)

    # =====================================================
    # News
    # =====================================================

    db.execute("""

    CREATE TABLE IF NOT EXISTS news(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        headline TEXT,

        url TEXT,

        sentiment REAL,

        published_at DATETIME

    )

    """)

    # =====================================================
    # Option Chain
    # =====================================================

    db.execute("""

    CREATE TABLE IF NOT EXISTS option_chain(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        expiry DATE,

        strike REAL,

        option_type TEXT,

        oi INTEGER,

        oi_change INTEGER,

        volume INTEGER,

        iv REAL,

        ltp REAL,

        updated_at DATETIME

    )

    """)

    # =====================================================
    # Settings
    # =====================================================

    db.execute("""

    CREATE TABLE IF NOT EXISTS settings(

        key TEXT PRIMARY KEY,

        value TEXT

    )

    """)

    print("TrendForge database created successfully.")
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

db.execute("""

CREATE INDEX IF NOT EXISTS idx_portfolio_sector

ON portfolio(sector)

""")