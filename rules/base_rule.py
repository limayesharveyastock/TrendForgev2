from abc import ABC, abstractmethod

from models.engine_result import RuleResult


class BaseRule(ABC):

    def __init__(self,
                 name,
                 field,
                 weight):

        self.name = name
        self.field = field
        self.weight = weight

    @abstractmethod
    def evaluate(self, stock):

        pass