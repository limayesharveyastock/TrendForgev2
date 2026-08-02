from sqlalchemy import (
    Column,
    Integer,
    String,
    Float
)

from database.base import Base


class Watchlist(Base):

    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)

    symbol = Column(String(20), unique=True)

    score = Column(Float)

    signal = Column(String(30))

    confidence = Column(Float)