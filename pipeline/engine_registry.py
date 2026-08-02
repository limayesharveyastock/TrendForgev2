class EngineRegistry:

    def __init__(self):

        self.engines = []

    def register(

        self,

        engine,

    ):

        self.engines.append(engine)

    def execute(

        self,

        symbol,

    ):

        results = {}

        for engine in self.engines:

            results[engine.NAME] = engine.evaluate(symbol)

        return results