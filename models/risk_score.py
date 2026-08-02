from dataclasses import dataclass, field


@dataclass(slots=True)
class RiskScore:

    score: float

    confidence: float

    stoploss: float

    target1: float

    target2: float

    target3: float

    rr: float

    quantity: int

    warnings: list[str] = field(default_factory=list)

    reasons: list[str] = field(default_factory=list)