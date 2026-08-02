from dataclasses import dataclass
from datetime import datetime


@dataclass
class CorporateEvent:

    symbol: str

    event_type: str

    title: str

    event_date: datetime

    impact: str

    source: str

    confidence: float

    metadata: dict