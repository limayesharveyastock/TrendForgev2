from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class EngineResult:
    engine: str
    passed: bool
    score: float
    confidence: float
    grade: str

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class BaseEngine(ABC):

    @abstractmethod
    def evaluate(self, stock: Dict) -> EngineResult:
        pass