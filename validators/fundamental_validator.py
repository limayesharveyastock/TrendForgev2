class FundamentalValidator:

    REQUIRED_FIELDS = [

        "roce",

        "roe",

        "pe",

        "industry_pe",

        "sales_growth",

        "profit_growth",

        "eps_growth",

        "debt_equity",

        "promoter_holding"

    ]

    def validate(self, data):

        missing = []

        for field in self.REQUIRED_FIELDS:

            if field not in data:

                missing.append(field)

        return len(missing) == 0, missing