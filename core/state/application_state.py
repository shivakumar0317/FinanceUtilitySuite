"""
Risk Management System
Shared Application State

Stores the active master portfolio dataset so every page can use the
same imported and processed data.

Author  : Shiva Kumar
Version : 2.0
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


class ApplicationState:
    """Central in-memory state for the RMS desktop application."""

    _master_portfolio: pd.DataFrame | None = None
    _source_file: str | None = None
    _imported_at: datetime | None = None

    @classmethod
    def set_master_portfolio(
        cls,
        dataframe: pd.DataFrame,
        source_file: str | None = None,
    ) -> None:
        if dataframe is None:
            raise ValueError("Master portfolio dataframe cannot be None.")

        cls._master_portfolio = dataframe.copy()
        cls._source_file = source_file
        cls._imported_at = datetime.now()

    @classmethod
    def get_master_portfolio(cls) -> pd.DataFrame | None:
        if cls._master_portfolio is None:
            return None

        return cls._master_portfolio.copy()

    @classmethod
    def has_master_portfolio(cls) -> bool:
        return (
            cls._master_portfolio is not None
            and not cls._master_portfolio.empty
        )

    @classmethod
    def clear(cls) -> None:
        cls._master_portfolio = None
        cls._source_file = None
        cls._imported_at = None

    @classmethod
    def get_source_file(cls) -> str | None:
        return cls._source_file

    @classmethod
    def get_source_filename(cls) -> str:
        if not cls._source_file:
            return ""

        return Path(cls._source_file).name

    @classmethod
    def get_imported_at(cls) -> datetime | None:
        return cls._imported_at

    @classmethod
    def get_summary(cls) -> dict:
        dataframe = cls._master_portfolio

        if dataframe is None or dataframe.empty:
            return {
                "records": 0,
                "clients": 0,
                "symbols": 0,
                "source_file": "",
                "imported_at": None,
            }

        clients = (
            dataframe["AccountId"].nunique()
            if "AccountId" in dataframe.columns
            else 0
        )

        symbols = (
            dataframe["Symbol"].nunique()
            if "Symbol" in dataframe.columns
            else 0
        )

        return {
            "records": len(dataframe),
            "clients": int(clients),
            "symbols": int(symbols),
            "source_file": cls.get_source_filename(),
            "imported_at": cls._imported_at,
        }