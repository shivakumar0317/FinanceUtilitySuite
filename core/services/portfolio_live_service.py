"""
Finance Utility Suite
Portfolio Live Service

Version: 1.20
"""

from __future__ import annotations

import pandas as pd

from core.services.market_data_service import MarketDataService


class PortfolioLiveService:

    REQUIRED_COLUMNS = (
        "SYMBOL",
        "QTY",
        "AVG_PRICE",
    )

    @classmethod
    def refresh_prices(
        cls,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        prices = []
        values = []
        pnl = []
        pnl_pct = []

        for _, row in df.iterrows():
            symbol = str(row["SYMBOL"])

            qty = float(row["QTY"])
            avg = float(row["AVG_PRICE"])

            ltp = MarketDataService.get_current_price(symbol)

            invested = qty * avg
            current = qty * ltp

            profit = current - invested

            profit_pct = (
                (profit / invested) * 100
                if invested
                else 0
            )

            prices.append(ltp)
            values.append(current)
            pnl.append(profit)
            pnl_pct.append(profit_pct)

        df["LTP"] = prices
        df["CURRENT_VALUE"] = values
        df["P/L"] = pnl
        df["P/L %"] = pnl_pct

        return df