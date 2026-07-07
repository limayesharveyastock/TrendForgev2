def migrate(db):

    db.execute("""

    CREATE TABLE IF NOT EXISTS backtest_results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        strategy_name TEXT,

        symbol TEXT,

        timeframe TEXT,

        start_date DATE,

        end_date DATE,

        total_trades INTEGER,

        win_rate REAL,

        net_profit REAL,

        max_drawdown REAL,

        sharpe_ratio REAL,

        created_at DATETIME

    )

    """)