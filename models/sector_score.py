from dataclasses import dataclass


@dataclass
class SectorScore:

    sector: str

    score: float

    rank: int

    confidence: float

    trend: str

    reasons: list