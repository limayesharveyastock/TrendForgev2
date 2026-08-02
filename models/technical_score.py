from dataclasses import dataclass, field


@dataclass(slots=True)
class TechnicalScore:

    total: float

    trend: float

    momentum: float

    volume: float

    volatility: float

    confirmation: float

    confidence: float

    signal: str

    grade: str

    reasons: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)