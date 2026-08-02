from database.session import SessionLocal
from database.models.watchlist import Watchlist


class WatchlistService:

    def save(self, signal):

        db = SessionLocal()

        item = Watchlist(

            symbol=signal.symbol,

            score=signal.overall_score,

            signal=signal.signal,

            confidence=signal.confidence

        )

        db.merge(item)

        db.commit()

        db.close()

    def all(self):

        db = SessionLocal()

        rows = db.query(Watchlist).all()

        db.close()

        return rows