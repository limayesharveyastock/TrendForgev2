from concurrent.futures import ThreadPoolExecutor, as_completed

from engines.market_regime_engine import MarketRegimeEngine
from engines.sector_strength_engine import SectorStrengthEngine
from engines.fundamental_engine import FundamentalEngine
from engines.corporate_action_engine import CorporateActionEngine
from engines.big_shark_engine import BigSharkEngine
from engines.technical_engine import TechnicalEngine
from engines.price_action_engine import PriceActionEngine
from engines.risk_engine import RiskEngine
from engines.signal_engine import SignalEngine


class ScannerEngine:

    def __init__(self):

        self.market = MarketRegimeEngine()
        self.sector = SectorStrengthEngine()
        self.fundamental = FundamentalEngine()
        self.corporate = CorporateActionEngine()
        self.shark = BigSharkEngine()
        self.technical = TechnicalEngine()
        self.price_action = PriceActionEngine()
        self.risk = RiskEngine()
        self.signal = SignalEngine()

    def scan(self, symbols, capital):

        market = self.market.evaluate()
        sectors = self.sector.evaluate()

        signals = []

        with ThreadPoolExecutor(max_workers=16) as executor:

            futures = {

                executor.submit(

                    self.scan_stock,

                    symbol,

                    market,

                    sectors,

                    capital

                ): symbol

                for symbol in symbols

            }

            for future in as_completed(futures):

                result = future.result()

                if result:

                    signals.append(result)

        signals.sort(

            key=lambda x: x.overall_score,

            reverse=True

        )

        return signals

    def scan_stock(

        self,

        symbol,

        market,

        sectors,

        capital,

    ):

        fundamental = self.fundamental.evaluate(symbol)

        corporate = self.corporate.evaluate(symbol)

        shark = self.shark.evaluate(symbol)

        technical = self.technical.evaluate(symbol)

        price_action = self.price_action.evaluate(symbol)

        risk = self.risk.evaluate(

            technical.snapshot,

            capital,

        )

        return self.signal.generate(

            symbol,

            market,

            sectors[technical.sector],

            fundamental,

            corporate,

            shark,

            technical,

            price_action,

            risk,

        )