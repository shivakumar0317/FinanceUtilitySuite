# Analytics Report Guide

## Input columns
Required: Symbol, Quantity, Average Price, Current Price.
Optional: Sector, Investment, Current Value, Profit, Return %.
Common aliases are normalized automatically.

## Workbook
- Dashboard: KPI cards, executive snapshot, Top Holdings chart, Sector Allocation chart.
- Summary: portfolio-level metrics.
- Chart Data: normalized calculation data, hidden after generation.

## Controller usage
```python
ReportController.generate_analytics(
    "analytics.xlsx",
    portfolio_df=dataframe,
    portfolio_name="My Portfolio",
)
```
