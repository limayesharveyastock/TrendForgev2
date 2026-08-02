from dataclasses import dataclass


@dataclass
class ScanContext:

    symbol: str

    stock: dict

    market: dict

    sector: dict

    fundamentals: dict

    corporate: dict

    technical: dict

    volume: dict

    news: dict