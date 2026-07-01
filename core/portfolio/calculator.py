"""
Finance Utility Suite
Portfolio Calculator
"""

from __future__ import annotations

import pandas as pd


class PortfolioCalculator:
    """
    Performs portfolio calculations.
    """

    @staticmethod
    def calculate(df: pd.DataFrame) -> pd.DataFrame:

        dataframe = df.copy()

        # -------------------------------------------------
        # Investment
        # -------------------------------------------------

        dataframe["Investment"] = (
            dataframe["Qty"] *
            dataframe["Buy Price"]
        )

        # -------------------------------------------------
        # Current Price
        #
        # Temporary:
        # Until Yahoo Finance integration,
        # assume current price = buy price.
        # -------------------------------------------------

        dataframe["Current Price"] = dataframe["Buy Price"]

        # -------------------------------------------------

        dataframe["Current Value"] = (
            dataframe["Qty"] *
            dataframe["Current Price"]
        )

        # -------------------------------------------------

        dataframe["Profit"] = (
            dataframe["Current Value"] -
            dataframe["Investment"]
        )

        # -------------------------------------------------

        dataframe["Return %"] = (
            dataframe["Profit"] /
            dataframe["Investment"]
        ) * 100

        dataframe["Return %"] = dataframe["Return %"].round(2)

        return dataframe

    # -----------------------------------------------------

    @staticmethod
    def summary(df: pd.DataFrame):

        return {

            "investment":
                df["Investment"].sum(),

            "current_value":
                df["Current Value"].sum(),

            "profit":
                df["Profit"].sum(),

            "holdings":
                len(df)
        }