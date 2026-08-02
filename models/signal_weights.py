from dataclasses import dataclass, field


@dataclass(slots=True)
class Signal:

    symbol:str

    signal:str

    confidence:float

    overall_score:float

    entry:float

    stoploss:float

    target1:float

    target2:float

    target3:float

    risk_reward:float

    reasons:list[str]=field(default_factory=list)

    warnings:list[str]=field(default_factory=list)