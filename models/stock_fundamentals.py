from dataclasses import dataclass


@dataclass
class StockFundamentals:

    symbol: str

    company_name: str

    sector: str

    industry: str

    market_cap: float

    pe: float
    industry_pe: float
    pb: float
    peg: float

    roce: float
    roe: float

    sales_growth: float
    profit_growth: float
    eps_growth: float

    debt_equity: float

    current_ratio: float

    operating_cashflow: float

    free_cashflow: float

    promoter_holding: float

    promoter_holding_prev: float

    pledged: float

    pledged_prev: float