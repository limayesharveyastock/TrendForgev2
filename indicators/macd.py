from indicators.base_indicator import BaseIndicator


class MACDIndicator(BaseIndicator):

    def calculate(self, df):

        ema12 = df.close.ewm(span=12).mean()

        ema26 = df.close.ewm(span=26).mean()

        macd = ema12 - ema26

        signal = macd.ewm(span=9).mean()

        hist = macd - signal

        return macd, signal, hist