from dataclasses import dataclass


@dataclass
class Shareholder:

    name: str

    category: str

    holding: float

    previous_holding: float

    change: float

    value: float

    quarter: str