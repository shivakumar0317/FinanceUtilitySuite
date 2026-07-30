from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from desktop.reports.report_export_service import (
    ReportExportError,
    ReportExportRequest,
    ReportExportService,
)


class ReportExportServiceTests(unittest.TestCase):
    def test_compact_portfolio_format_is_normalised_and_enriched(self):
        source = pd.DataFrame(
            {
                "Symbol": ["RELIANCE", "TCS"],
                "Qty": [2, 3],
                "Buy Price": [2500.0, 3500.0],
            }
        )
        prices = {"RELIANCE": 3000.0, "TCS": 4000.0}

        with patch.object(
            ReportExportService,
            "_get_current_price",
            side_effect=lambda symbol: prices[symbol],
        ):
            result = ReportExportService.prepare_portfolio_dataframe(source)

        self.assertEqual(
            ["Symbol", "Quantity", "Average Price", "Current Price"],
            [column for column in result.columns if column in {
                "Symbol", "Quantity", "Average Price", "Current Price"
            }],
        )
        self.assertEqual(result["Current Price"].tolist(), [3000.0, 4000.0])

    def test_existing_current_price_does_not_call_market_service(self):
        source = pd.DataFrame(
            {
                "Symbol": ["INFY"],
                "Qty": [5],
                "Buy Price": [1200.0],
                "CMP": [1500.0],
            }
        )
        with patch.object(ReportExportService, "_get_current_price") as fetch:
            result = ReportExportService.prepare_portfolio_dataframe(source)
        fetch.assert_not_called()
        self.assertEqual(float(result.loc[0, "Current Price"]), 1500.0)

    def test_missing_compact_input_column_fails_cleanly(self):
        source = pd.DataFrame({"Symbol": ["TCS"], "Qty": [1]})
        with self.assertRaisesRegex(ReportExportError, "Average Price"):
            ReportExportService.prepare_portfolio_dataframe(source)

    def test_request_adds_xlsx_extension(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "portfolio.csv"
            source.write_text("Symbol,Qty,Buy Price\nTCS,1,100\n", encoding="utf-8")
            request = ReportExportRequest(
                report_id="portfolio",
                source_path=source,
                output_path=Path(folder) / "output",
            )
            self.assertEqual(request.output_path.suffix, ".xlsx")

    def test_invalid_price_fails_cleanly(self):
        source = pd.DataFrame(
            {"Symbol": ["TCS"], "Qty": [1], "Buy Price": [100.0]}
        )
        with patch.object(ReportExportService, "_get_current_price", return_value=0):
            with self.assertRaisesRegex(ReportExportError, "Current price"):
                ReportExportService.prepare_portfolio_dataframe(source)


if __name__ == "__main__":
    unittest.main()
