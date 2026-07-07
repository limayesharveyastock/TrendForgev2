CREATE TABLE ai_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    scanner TEXT,
    signal TEXT,
    score REAL,
    entry_price REAL,
    exit_price REAL,
    outcome TEXT,
    pnl REAL,
    feedback_date DATETIME
);