"""
optimizer.py
----------------------------------------------------------
TrendForge Strategy Optimizer

Features
--------
- Grid Search Optimization
- Parameter Combination Testing
- Best Strategy Selection
- Backtest Integration
- Ranking by Return
- Ranking by Win Rate
- Ranking by Profit Factor
"""

from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Callable

from backtesting_engine import BacktestingEngine


# ==========================================================
# RESULT
# ==========================================================

@dataclass
class OptimizationResult:

    parameters: Dict

    return_percent: float

    win_rate: float

    profit_factor: float

    net_profit: float


# ==========================================================
# OPTIMIZER
# ==========================================================

class StrategyOptimizer:

    def __init__(self):

        self.results: List[OptimizationResult] = []

    # ------------------------------------------------------

    def optimize(
        self,
        symbol,
        historical_data,
        parameter_space: Dict[str, List],
        signal_provider_factory: Callable
    ):

        self.results.clear()

        keys = list(parameter_space.keys())

        values = list(parameter_space.values())

        for combination in product(*values):

            params = dict(zip(keys, combination))

            signal_provider = signal_provider_factory(
                params
            )

            engine = BacktestingEngine()

            engine.run(
                symbol=symbol,
                price_data=historical_data,
                signal_provider=signal_provider
            )

            report = engine.final_report()

            result = OptimizationResult(

                parameters=params,

                return_percent=report.get(
                    "Return (%)", 0
                ),

                win_rate=report.get(
                    "Win Rate (%)", 0
                ),

                profit_factor=report.get(
                    "Profit Factor", 0
                ),

                net_profit=report.get(
                    "Net Profit", 0
                )

            )

            self.results.append(result)

        self.results.sort(

            key=lambda x: (
                x.return_percent,
                x.profit_factor,
                x.win_rate
            ),

            reverse=True

        )

        return self.results

    # ------------------------------------------------------

    def best(self):

        if not self.results:

            return None

        return self.results[0]

    # ------------------------------------------------------

    def top(self, n=10):

        return self.results[:n]

    # ------------------------------------------------------

    def summary(self):

        if not self.results:

            return []

        output = []

        for result in self.results:

            output.append({

                "Parameters": result.parameters,

                "Return (%)": result.return_percent,

                "Win Rate (%)": result.win_rate,

                "Profit Factor": result.profit_factor,

                "Net Profit": result.net_profit

            })

        return output