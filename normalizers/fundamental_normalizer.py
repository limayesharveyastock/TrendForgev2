class FundamentalNormalizer:

    def normalize(self, raw):

        normalized = {}

        normalized["symbol"] = raw.get("symbol")

        normalized["company_name"] = raw.get("company_name")

        normalized["sector"] = raw.get("sector", "").upper()

        normalized["industry"] = raw.get("industry", "").upper()

        normalized["roce"] = float(raw.get("roce", 0))

        normalized["roe"] = float(raw.get("roe", 0))

        normalized["pe"] = float(raw.get("pe", 0))

        normalized["industry_pe"] = float(raw.get("industry_pe", 0))

        normalized["sales_growth"] = float(raw.get("sales_growth", 0))

        normalized["profit_growth"] = float(raw.get("profit_growth", 0))

        normalized["eps_growth"] = float(raw.get("eps_growth", 0))

        normalized["debt_equity"] = float(raw.get("debt_equity", 999))

        normalized["promoter_holding"] = float(raw.get("promoter_holding", 0))

        normalized["pledged"] = float(raw.get("pledged", 100))

        return normalized