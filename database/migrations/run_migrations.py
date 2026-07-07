from database.database import Database

from database.migrations import (
    instruments,
    fundamentals,
    corporate_actions,
    scanner_results,
    watchlists,
    alerts,
    trade_history,
    portfolio,
    news,
    option_chain,
    settings,
    backtest_results,
    ai_feedback,
)


def run():

    db = Database()

    migrations = [
        instruments,
        fundamentals,
        corporate_actions,
        scanner_results,
        watchlists,
        alerts,
        trade_history,
        portfolio,
        news,
        option_chain,
        settings,
        backtest_results,
        ai_feedback,
    ]

    for migration in migrations:
        migration.migrate(db)

    print("✅ TrendForge database initialized successfully.")


if __name__ == "__main__":
    run()