class ProviderFactory:

    def __init__(

        self,

        kite=None,

        yahoo=None,

        nse=None,

    ):

        self.kite = kite

        self.yahoo = yahoo

        self.nse = nse

    def market_data(self):

        if self.kite:

            return self.kite

        return self.yahoo

    def quote(self):

        if self.kite:

            return self.kite

        return self.nse