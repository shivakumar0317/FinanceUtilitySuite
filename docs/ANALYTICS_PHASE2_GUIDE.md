# Analytics Report Phase 2

Version 1.38.1 adds a professional multi-sheet analytics workbook.

## Workbook sheets

- Dashboard: KPI cards, executive snapshot, top holdings and sector allocation charts.
- Performance Summary: portfolio return, winner/loser counts, best/worst holdings and optional CAGR.
- Monthly Returns: monthly and yearly performance with conditional formatting and a chart.
- Sector Analysis: allocation, return and contribution by sector with a chart.
- Top Performers: top winners and losers with contribution metrics.
- Summary: machine-readable KPI list.
- Chart Data: hidden supporting data.

## Optional historical data

Pass a dataframe containing `Date` and `Portfolio Value`:

```python
ReportController.generate_analytics(
    "analytics.xlsx",
    portfolio_df=holdings,
    history_df=history,
    portfolio_name="My Portfolio",
)
```

Supported history aliases include Timestamp/Valuation Date and NAV/Current Value.
The report still exports when historical data is omitted.
