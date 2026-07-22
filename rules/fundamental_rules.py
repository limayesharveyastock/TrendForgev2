from rules.roce_rule import ROCERule

from rules.roe_rule import ROERule

# Next

# SalesGrowthRule

# ProfitGrowthRule

# EPSGrowthRule

# DebtRule

# PEGRule

# PERule

# CashFlowRule

# PromoterRule

# PledgeRule


FUNDAMENTAL_RULES = [

    ROCERule(),

    ROERule(),

    SalesGrowthRule(),

    ProfitGrowthRule(),

    EPSGrowthRule(),

    DebtEquityRule(),

    CurrentRatioRule(),

    OperatingCashFlowRule(),

]