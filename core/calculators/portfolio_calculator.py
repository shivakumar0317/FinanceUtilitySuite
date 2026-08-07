"""
Finance Utility Suite
Enterprise RMS

Module:
    portfolio_calculator.py

Description:
    Calculates portfolio-level metrics from the MTF dataframe.

Author:
    OpenAI

Version:
    3.0
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class PortfolioMetrics:
    """
    Portfolio level metrics.

    Attributes
    ----------
    records
        Total dataframe rows.

    clients
        Unique client count.

    symbols
        Unique symbol count.

    portfolio_value
        Sum of NetValue.

    total_exposure
        Total portfolio exposure.

    total_mtm
        Total Mark To Market.

    total_buy_value
        Sum of BUY VALUE.

    total_var
        Sum of MTF VAR.

    total_margin
        Sum of MTF MARGIN.
    """

    records: int
    clients: int
    symbols: int

    portfolio_value: float
    total_exposure: float

    total_mtm: float

    total_buy_value: float

    total_var: float

    total_margin: float


class PortfolioCalculator:
    """
    Portfolio metrics calculator.
    """

    REQUIRED_COLUMNS = (
        "AccountId",
        "Symbol",
        "NetValue",
        "MarkToMarket",
    )

    @classmethod
    def calculate(
        cls,
        dataframe: pd.DataFrame,
    ) -> PortfolioMetrics:
        """
        Calculate portfolio metrics.

        Parameters
        ----------
        dataframe
            RMS MTF dataframe.

        Returns
        -------
        PortfolioMetrics
        """

        cls._validate_dataframe(dataframe)

        return PortfolioMetrics(
            records=len(dataframe),

            clients=dataframe["AccountId"].nunique(),

            symbols=dataframe["Symbol"].nunique(),

            portfolio_value=cls._sum(
                dataframe,
                "NetValue",
            ),

            total_exposure=cls._calculate_exposure(
                dataframe,
            ),

            total_mtm=cls._sum(
                dataframe,
                "MarkToMarket",
            ),

            total_buy_value=cls._sum(
                dataframe,
                "BUY VALUE",
            ),

            total_var=cls._sum(
                dataframe,
                "MTF VAR",
            ),

            total_margin=cls._sum(
                dataframe,
                "MTF MARGIN",
            ),
        )

    @classmethod
    def _calculate_exposure(
        cls,
        dataframe: pd.DataFrame,
    ) -> float:
        """
        Calculate portfolio exposure.

        Uses BUY VALUE for current RMS exports.
        Falls back to NetValue for legacy snapshots.
        """

        if "BUY VALUE" in dataframe.columns:
            return cls._sum(
            dataframe,
            "BUY VALUE",
        )

        return cls._sum(
            dataframe,
            "NetValue",
        )

    @classmethod
    def _validate_dataframe(
        cls,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate dataframe.
        """

        if dataframe is None:
            raise ValueError("DataFrame is None.")

        if dataframe.empty:
            raise ValueError("DataFrame is empty.")

        missing = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}"
            )

    @staticmethod
    def _sum(
        dataframe: pd.DataFrame,
        column: str,
    ) -> float:
        """
        Safely sum a numeric column.
        Returns 0.0 if the column does not exist.
        """

        if column not in dataframe.columns:
            return 0.0

        return float(
            pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )
        .fillna(0)
        .sum()
    )