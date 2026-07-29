from __future__ import annotations

import unittest
from datetime import datetime

import pandas as pd

from desktop.reports.performance_engine import PerformanceDataError, PerformanceEngine


class PerformanceEngineTests(unittest.TestCase):
    @staticmethod
    def holdings() -> pd.DataFrame:
        return pd.DataFrame([
            {"Symbol": "ALPHA", "Quantity": 10, "Average Price": 100, "Current Price": 130, "Sector": "Technology"},
            {"Symbol": "BETA", "Quantity": 20, "Average Price": 50, "Current Price": 45, "Sector": "Finance"},
            {"Symbol": "GAMMA", "Quantity": 5, "Average Price": 200, "Current Price": 200, "Sector": "Technology"},
            {"Symbol": "ALPHA", "Quantity": 2, "Average Price": 110, "Current Price": 130, "Sector": "Technology"},
        ])

    @staticmethod
    def history() -> pd.DataFrame:
        return pd.DataFrame({
            "Date": ["2024-01-01", "2024-01-31", "2024-02-29", "2025-01-31"],
            "Portfolio Value": [100000, 110000, 121000, 133100],
        })

    def setUp(self) -> None:
        self.engine = PerformanceEngine()

    def test_summary_counts_and_rankings(self):
        result = self.engine.calculate_summary(self.holdings())
        self.assertEqual(result.winners, 1)
        self.assertEqual(result.losers, 1)
        self.assertEqual(result.breakeven, 1)
        self.assertEqual(result.best_stock, "ALPHA")
        self.assertEqual(result.worst_stock, "BETA")

    def test_duplicate_holdings_are_consolidated(self):
        frame = self.engine.prepare_holdings(self.holdings())
        alpha = frame.loc[frame["Symbol"] == "ALPHA"].iloc[0]
        self.assertEqual(float(alpha["Quantity"]), 12.0)

    def test_top_gainers_and_losers(self):
        self.assertEqual(self.engine.top_gainers(self.holdings(), 1).iloc[0]["Symbol"], "ALPHA")
        self.assertEqual(self.engine.top_losers(self.holdings(), 1).iloc[0]["Symbol"], "BETA")

    def test_invalid_ranking_limit(self):
        with self.assertRaises(PerformanceDataError):
            self.engine.top_gainers(self.holdings(), 0)

    def test_holding_contribution_sums_to_portfolio_return(self):
        frame = self.engine.holding_contribution(self.holdings())
        expected = frame["Profit"].sum() / frame["Investment"].sum() * 100
        self.assertAlmostEqual(float(frame["Contribution %"].sum()), expected, places=8)

    def test_sector_performance(self):
        frame = self.engine.sector_performance(self.holdings())
        self.assertEqual(set(frame["Sector"]), {"Technology", "Finance"})
        self.assertEqual(frame.iloc[0]["Sector"], "Technology")

    def test_history_aliases_and_duplicate_dates(self):
        data = pd.DataFrame({"Timestamp": ["2025-01-01", "2025-01-01"], "NAV": [100, 105]})
        frame = self.engine.prepare_history(data)
        self.assertEqual(len(frame), 1)
        self.assertEqual(float(frame.iloc[0]["Portfolio Value"]), 105.0)

    def test_portfolio_growth(self):
        frame = self.engine.portfolio_growth(self.history())
        self.assertAlmostEqual(float(frame.iloc[-1]["Cumulative Return %"]), 33.1, places=3)

    def test_monthly_returns(self):
        frame = self.engine.monthly_returns(self.history())
        feb = frame.loc[frame["Period"] == "2024-02"].iloc[0]
        self.assertAlmostEqual(float(feb["Return %"]), 10.0, places=4)

    def test_yearly_returns(self):
        frame = self.engine.yearly_returns(self.history())
        self.assertEqual(list(frame["Year"]), [2024, 2025])
        self.assertAlmostEqual(float(frame.iloc[1]["Return %"]), 10.0, places=4)

    def test_cagr(self):
        history = pd.DataFrame({
            "Date": [datetime(2024, 1, 1), datetime(2025, 1, 1)],
            "Portfolio Value": [100, 121],
        })
        self.assertAlmostEqual(self.engine.cagr(history), 20.9523, places=4)

    def test_empty_holdings(self):
        with self.assertRaises(PerformanceDataError):
            self.engine.calculate_summary(pd.DataFrame())

    def test_missing_history_columns(self):
        with self.assertRaises(PerformanceDataError):
            self.engine.monthly_returns(pd.DataFrame({"Date": ["2025-01-01"]}))


if __name__ == "__main__":
    unittest.main()
