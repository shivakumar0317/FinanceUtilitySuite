# Performance Engine Guide — v1.38.1 Phase 1

`PerformanceEngine` adds reusable performance calculations without changing the stable report framework.

## Holdings APIs

- `calculate_summary(dataframe)`
- `top_gainers(dataframe, limit=10)`
- `top_losers(dataframe, limit=10)`
- `holding_contribution(dataframe)`
- `sector_performance(dataframe)`

Required holdings fields are the same as `PortfolioAnalyticsEngine`: Symbol, Quantity, Average Price, and Current Price. Existing aliases remain supported.

## Historical APIs

Historical data requires a date and portfolio-value column. Common aliases such as `Timestamp`, `NAV`, `Market Value`, and `Current Value` are accepted.

- `portfolio_growth(history)`
- `monthly_returns(history)`
- `yearly_returns(history)`
- `cagr(history)`

Phase 1 integrates best/worst holding and sector results into the existing Analytics Dashboard and Summary sheet. New performance worksheets and charts are reserved for Phase 2.
