from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from database.base import Base


class SignalHistory(Base):

    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True)

    symbol = Column(String(20), index=True)

    timeframe = Column(String(20))

    signal = Column(String(30))

    score = Column(Float)

    confidence = Column(Float)

    entry = Column(Float)

    stoploss = Column(Float)

    target1 = Column(Float)

    target2 = Column(Float)

    target3 = Column(Float)

    created_at = Column(DateTime)