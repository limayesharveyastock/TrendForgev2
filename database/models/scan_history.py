from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Integer as Int
)

from database.base import Base


class ScanHistory(Base):

    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True)

    scan_time = Column(DateTime)

    scanned = Column(Int)

    buy = Column(Int)

    strong_buy = Column(Int)

    watchlist = Column(Int)

    sell = Column(Int)