class ExitRule:

    def calculate(self, risk):

        return {

            "sl": risk.stoploss,

            "t1": risk.target1,

            "t2": risk.target2,

            "t3": risk.target3,

        }