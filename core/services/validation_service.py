from __future__ import annotations

from dataclasses import dataclass, field
import pandas as pd


@dataclass(slots=True)
class ValidationReport:
    required_columns_found: list[str] = field(default_factory=list)
    optional_columns_found: list[str] = field(default_factory=list)
    optional_columns_missing: list[str] = field(default_factory=list)
    auto_created_columns: list[str] = field(default_factory=list)
    preserved_broker_columns: list[str] = field(default_factory=list)
    records_received: int = 0
    records_after_cleaning: int = 0

    @property
    def is_valid(self) -> bool:
        return bool(self.required_columns_found)


class ValidationService:
    REQUIRED_COLUMNS = (
        "AccountId", "Symbol", "NetQty", "BUY VALUE",
        "NetValue", "MarkToMarket", "MTF VAR", "MTF MARGIN",
    )

    OPTIONAL_COLUMNS = (
        "Exposure", "LastTradedPrice", "BuyAvgPrice",
        "NetBuyQty", "NetSellQty", "Company Name",
        "Sector", "Industry", "Beta", "Market Cap",
    )

    BROKER_COLUMNS = (
        "LastTradedPrice", "BuyAvgPrice", "NetBuyQty", "NetSellQty",
    )

    @classmethod
    def validate_dataframe(cls, dataframe: pd.DataFrame) -> ValidationReport:
        if dataframe is None:
            raise ValueError("Imported dataframe cannot be None.")
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Imported data must be a pandas DataFrame.")
        if dataframe.empty:
            raise ValueError("The selected file does not contain any data.")

        columns = {str(c).strip() for c in dataframe.columns}
        missing = [c for c in cls.REQUIRED_COLUMNS if c not in columns]
        if missing:
            raise ValueError(
                "The selected file is missing required columns:\n\n• "
                + "\n• ".join(missing)
            )

        return ValidationReport(
            required_columns_found=list(cls.REQUIRED_COLUMNS),
            optional_columns_found=[c for c in cls.OPTIONAL_COLUMNS if c in columns],
            optional_columns_missing=[c for c in cls.OPTIONAL_COLUMNS if c not in columns],
            preserved_broker_columns=[c for c in cls.BROKER_COLUMNS if c in columns],
            records_received=len(dataframe),
        )

    @staticmethod
    def validate_cleaned_dataframe(dataframe: pd.DataFrame) -> None:
        if dataframe is None or dataframe.empty:
            raise ValueError("No valid portfolio records remain after cleaning.")
        for column in ("AccountId", "Symbol"):
            if column not in dataframe.columns:
                raise ValueError(f"Cleaned data is missing {column}.")
            empty = dataframe[column].fillna("").astype(str).str.strip().eq("").sum()
            if empty:
                raise ValueError(f"{empty} records contain an empty {column}.")

    @classmethod
    def build_import_report(
        cls,
        raw_dataframe: pd.DataFrame,
        cleaned_dataframe: pd.DataFrame,
    ) -> ValidationReport:
        report = cls.validate_dataframe(raw_dataframe)
        report.records_after_cleaning = len(cleaned_dataframe)
        if "Exposure" not in raw_dataframe.columns and "Exposure" in cleaned_dataframe.columns:
            report.auto_created_columns.append("Exposure")
        return report
