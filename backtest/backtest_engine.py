from dataclasses import dataclass
from typing import List

from backtest.trade import Trade
from backtest.performance_metrics import PerformanceMetrics


@dataclass(slots=True)
class BacktestResult:

    trades: List[Trade]

    metrics: PerformanceMetrics


class BacktestEngine:

    def __init__(self, strategy):

        self.strategy = strategy

    def run(self, data):

        trades = self.strategy.execute(data)

        metrics = PerformanceMetrics(trades)

        return BacktestResult(

            trades=trades,

            metrics=metrics

        )