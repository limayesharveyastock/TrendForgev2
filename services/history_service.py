from database.session import SessionLocal
from database.models.signal_history import SignalHistory


class HistoryService:

    def save(self, signal):

        db = SessionLocal()

        row = SignalHistory(

            symbol=signal.symbol,

            timeframe=signal.timeframe,

            signal=signal.signal,

            score=signal.overall_score,

            confidence=signal.confidence,

            entry=signal.entry,

            stoploss=signal.stoploss,

            target1=signal.target1,

            target2=signal.target2,

            target3=signal.target3,

            created_at=signal.timestamp

        )

        db.add(row)

        db.commit()

        db.close()