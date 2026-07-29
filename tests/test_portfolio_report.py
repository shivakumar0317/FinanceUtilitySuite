from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from desktop.reports.portfolio_report import PortfolioReport

df = pd.DataFrame({
    "Symbol": ["RELIANCE", "INFY", "TCS"],
    "Sector": ["Oil & Gas", "IT", "IT"],
    "Quantity": [10, 20, 5],
    "Avg Price": [2500, 1400, 3600],
    "Current Price": [2700, 1550, 3750],
    "Investment": [25000, 28000, 18000],
    "Current Value": [27000, 31000, 18750],
    "Profit/Loss": [2000, 3000, 750],
    "Return %": [8.0, 10.7, 4.2],
})

report = PortfolioReport(df)

report.export("Portfolio_Test.xlsx")

print("Portfolio report generated successfully.")