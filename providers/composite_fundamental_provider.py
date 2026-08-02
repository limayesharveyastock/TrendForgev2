from typing import Dict, Optional

from providers.fundamental_provider import FundamentalProvider


class CompositeFundamentalProvider(FundamentalProvider):

    def __init__(self, providers):
        self.providers = providers

    def get_fundamentals(self, symbol: str) -> Optional[Dict]:

        for provider in self.providers:

            try:

                data = provider.get_fundamentals(symbol)

                if data:

                    return data

            except Exception:

                continue

        return None