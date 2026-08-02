from typing import List

from models.engine_result import EngineResult


class TrendForgePipeline:

    def __init__(self):

        self.engines: List = []

    def register(self, engine):

        self.engines.append(engine)

    def execute(self, stock):

        results = []

        total_score = 0
        total_max = 0

        for engine in self.engines:

            result = engine.evaluate(stock)

            results.append(result)

            total_score += result.score
            total_max += result.max_score

            # HARD STOP

            if not result.passed:

                break

        return {

            "results": results,

            "score": total_score,

            "max_score": total_max

        }