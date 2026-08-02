from dataclasses import dataclass


@dataclass
class SectorSnapshot:

    sector: str

    index_price: float

    change_1d: float

    change_1w: float

    change_1m: float

    change_3m: float

    volume_ratio: float

    relative_strength: float

    advancing: int

    declining: int

    fii_flow: float

    dii_flow: float

    leadership_score: float