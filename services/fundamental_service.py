from normalizers.fundamental_normalizer import FundamentalNormalizer
from validators.fundamental_validator import FundamentalValidator


class FundamentalService:

    def __init__(self, provider):

        self.provider = provider

        self.normalizer = FundamentalNormalizer()

        self.validator = FundamentalValidator()

    def load(self, symbol):

        raw = self.provider.get_fundamentals(symbol)

        if raw is None:

            return None

        data = self.normalizer.normalize(raw)

        valid, missing = self.validator.validate(data)

        if not valid:

            raise Exception(f"Missing fields : {missing}")

        return data