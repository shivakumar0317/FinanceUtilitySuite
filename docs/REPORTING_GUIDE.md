# Portfolio Reporting Guide

The Portfolio Report accepts a pandas DataFrame and normalizes common aliases
for symbol, quantity, average price, current price, investment, current value,
profit, return percentage and sector.

Derived fields are recalculated when absent. Duplicate symbols are consolidated
before the report is produced.

The final workbook contains:

1. Dashboard
2. Holdings
3. Performance
4. Allocation
5. Hidden Chart Data
