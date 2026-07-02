"""
Finance Utility Suite
MTF Service

Business logic for Margin Trading Facility (MTF).

Author : Shiva Kumar
Version : 0.95
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class MTFService:
    """Business logic for MTF Analyzer."""

    REQUIRED_COLUMNS = [
        "AccountId",
        "Symbol",
        "BUY VALUE",
        "NetValue",
        "MarkToMarket",
        "MTF VAR",
        "MTF MARGIN",
    ]

    @classmethod
    def load(cls, file_path: str | Path):
        """Load MTF Excel / CSV."""

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            dataframe = pd.read_csv(file_path)

        elif suffix in (".xlsx", ".xls"):
            dataframe = pd.read_excel(file_path)

        else:
            raise ValueError("Unsupported file format.")

        dataframe.columns = dataframe.columns.str.strip()

        cls.validate_dataframe(dataframe)

        summary = cls.calculate_summary(dataframe)

        return dataframe, summary

    @classmethod
    def validate_dataframe(cls, dataframe: pd.DataFrame) -> None:
        """Validate required columns."""

        missing = [
            column for column in cls.REQUIRED_COLUMNS if column not in dataframe.columns
        ]

        if missing:
            raise ValueError("Missing required columns:\n\n" + "\n".join(missing))

    @classmethod
    def calculate_summary(cls, dataframe: pd.DataFrame) -> dict:
        """Calculate dashboard summary."""

        total_clients = dataframe["AccountId"].nunique()

        total_positions = len(dataframe)

        buy_value = dataframe["BUY VALUE"].sum()

        market_value = dataframe["NetValue"].sum()

        mtm = dataframe["MarkToMarket"].sum()

        avg_margin = dataframe["MTF MARGIN"].mean()

        avg_var = dataframe["MTF VAR"].mean()

        return {
            "clients": total_clients,
            "positions": total_positions,
            "buy_value": buy_value,
            "market_value": market_value,
            "mtm": mtm,
            "avg_margin": round(avg_margin, 2),
            "avg_var": round(avg_var, 2),
        }

    @classmethod
    def top_exposure(cls, dataframe: pd.DataFrame, limit: int = 10):
        """Top clients by BUY VALUE."""

        return (
            dataframe.groupby("AccountId", as_index=False)["BUY VALUE"]
            .sum()
            .sort_values(
                by="BUY VALUE",
                ascending=False,
            )
            .head(limit)
        )

    @classmethod
    def top_mtm_gainers(cls, dataframe: pd.DataFrame, limit: int = 10):
        """Top MTM gainers."""

        return dataframe.sort_values(
            by="MarkToMarket",
            ascending=False,
        ).head(limit)

    @classmethod
    def top_mtm_losers(cls, dataframe: pd.DataFrame, limit: int = 10):
        """Top MTM losers."""

        return dataframe.sort_values(
            by="MarkToMarket",
            ascending=True,
        ).head(limit)

    @classmethod
    def symbol_exposure(cls, dataframe: pd.DataFrame):
        """Exposure by symbol."""

        return (
            dataframe.groupby("Symbol", as_index=False)["BUY VALUE"]
            .sum()
            .sort_values(
                by="BUY VALUE",
                ascending=False,
            )
        )
