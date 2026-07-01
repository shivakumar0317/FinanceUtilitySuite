"""
Finance Utility Suite
Portfolio Loader
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class PortfolioLoader:
    """
    Loads portfolio files from Excel or CSV.
    """

    REQUIRED_COLUMNS = [
        "Symbol",
        "Qty",
        "Buy Price"
    ]

    @classmethod
    def load(cls, file_path: str) -> pd.DataFrame:

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        suffix = file_path.suffix.lower()

        if suffix == ".xlsx":
            df = pd.read_excel(file_path)

        elif suffix == ".csv":
            df = pd.read_csv(file_path)

        else:
            raise ValueError(
                "Unsupported file format."
            )

        df.columns = [c.strip() for c in df.columns]

        cls.validate(df)

        return df

    @classmethod
    def validate(cls, dataframe: pd.DataFrame):

        missing = []

        for column in cls.REQUIRED_COLUMNS:

            if column not in dataframe.columns:
                missing.append(column)

        if missing:

            raise ValueError(
                "Missing columns:\n\n"
                + "\n".join(missing)
            )