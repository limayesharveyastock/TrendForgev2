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
db.execute("""

CREATE INDEX IF NOT EXISTS idx_watchlist_name

ON watchlists(watchlist)

""")

db.execute("""

CREATE INDEX IF NOT EXISTS idx_watchlist_symbol

ON watchlists(symbol)

""")