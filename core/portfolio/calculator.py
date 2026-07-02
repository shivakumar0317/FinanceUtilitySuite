"""
Finance Utility Suite
Portfolio Calculator
"""

from __future__ import annotations

import pandas as pd

from core.services.market_data_service import MarketDataService


class PortfolioCalculator:
    """
    Performs portfolio calculations using live market prices.
    """

    @staticmethod
    def calculate(df: pd.DataFrame) -> pd.DataFrame:

        dataframe = df.copy()

        # Clean numeric columns
        dataframe["Qty"] = pd.to_numeric(dataframe["Qty"])
        dataframe["Buy Price"] = pd.to_numeric(dataframe["Buy Price"])

        current_prices = []

        print("\nFetching Live Prices...\n")

        for symbol in dataframe["Symbol"]:

            price = MarketDataService.get_current_price(symbol)

            print(f"{symbol:<15} ₹{price:,.2f}")

            current_prices.append(price)

        dataframe["Current Price"] = current_prices

        dataframe["Investment"] = dataframe["Qty"] * dataframe["Buy Price"]

        dataframe["Current Value"] = dataframe["Qty"] * dataframe["Current Price"]

        dataframe["Profit"] = dataframe["Current Value"] - dataframe["Investment"]

        dataframe["Return %"] = (
            dataframe["Profit"] / dataframe["Investment"] * 100
        ).round(2)

        dataframe["Current Price"] = dataframe["Current Price"].round(2)
        dataframe["Investment"] = dataframe["Investment"].round(2)
        dataframe["Current Value"] = dataframe["Current Value"].round(2)
        dataframe["Profit"] = dataframe["Profit"].round(2)
        dataframe["Return %"] = dataframe["Return %"].round(2)

        return dataframe

    @staticmethod
    def summary(df: pd.DataFrame):

        investment = df["Investment"].sum()
        current = df["Current Value"].sum()
        profit = df["Profit"].sum()

        return {
            "investment": investment,
            "current_value": current,
            "profit": profit,
            "return_percent": (
                round((profit / investment) * 100, 2) if investment else 0
            ),
            "holdings": len(df),
        }
