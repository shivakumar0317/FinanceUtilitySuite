"""
Risk Management System (RMS)
Master Import Service

Reads, validates, cleans and stores the active MTF portfolio dataset.

Author  : Shiva Kumar
Project : Risk Management System
Version : 2.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from core.services.data_cleaner import DataCleaner
from core.services.snapshot_service import SnapshotService
from core.services.validation_service import ValidationService
from core.state.application_state import ApplicationState


@dataclass(slots=True)
class ImportResult:
    """Structured result returned after a successful import."""

    dataframe: pd.DataFrame
    summary: dict[str, Any]
    source_file: str
    snapshot_id: str | None = None


class MasterImportService:
    """Central import engine used by all RMS modules."""

    SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

    @classmethod
    def import_file(cls, file_path: str | Path) -> ImportResult:
        """
        Import, validate, clean and store an MTF portfolio file.

        Parameters
        ----------
        file_path:
            Excel or CSV file selected by the user.

        Returns
        -------
        ImportResult
            Cleaned dataframe, import summary and source path.
        """

        path = Path(file_path)

        cls._validate_file(path)

        raw_dataframe = cls._read_file(path)

        ValidationService.validate_dataframe(raw_dataframe)

        cleaned_dataframe = DataCleaner.clean_master_portfolio(raw_dataframe)

        ValidationService.validate_cleaned_dataframe(cleaned_dataframe)

        ApplicationState.set_master_portfolio(
            cleaned_dataframe,
            source_file=str(path),
        )

        summary = cls.build_summary(cleaned_dataframe)

        snapshot = SnapshotService().create_snapshot(
            cleaned_dataframe,
            source_file=str(path),
        )

        return ImportResult(
            dataframe=cleaned_dataframe.copy(),
            summary=summary,
            source_file=str(path),
            snapshot_id=snapshot.snapshot_id,
        )

    @classmethod
    def import_dataframe(
        cls,
        dataframe: pd.DataFrame,
        source_name: str = "In-memory DataFrame",
    ) -> ImportResult:
        """Validate, clean and store an already-loaded dataframe."""

        ValidationService.validate_dataframe(dataframe)

        cleaned_dataframe = DataCleaner.clean_master_portfolio(dataframe)

        ValidationService.validate_cleaned_dataframe(cleaned_dataframe)

        ApplicationState.set_master_portfolio(
            cleaned_dataframe,
            source_file=source_name,
        )

        snapshot = SnapshotService().create_snapshot(
            cleaned_dataframe,
            source_file=source_name,
        )

        return ImportResult(
            dataframe=cleaned_dataframe.copy(),
            summary=cls.build_summary(cleaned_dataframe),
            source_file=source_name,
            snapshot_id=snapshot.snapshot_id,
        )

    @staticmethod
    def build_summary(dataframe: pd.DataFrame) -> dict[str, Any]:
        """Create a compact summary for dashboards and status messages."""

        if dataframe is None or dataframe.empty:
            return {
                "records": 0,
                "clients": 0,
                "symbols": 0,
                "total_exposure": 0.0,
                "total_mtm": 0.0,
                "total_buy_value": 0.0,
            }

        return {
            "records": int(len(dataframe)),
            "clients": MasterImportService._nunique(
                dataframe,
                "AccountId",
            ),
            "symbols": MasterImportService._nunique(
                dataframe,
                "Symbol",
            ),
            "total_exposure": MasterImportService._sum(
                dataframe,
                "Exposure",
            ),
            "total_mtm": MasterImportService._sum(
                dataframe,
                "MarkToMarket",
            ),
            "total_buy_value": MasterImportService._sum(
                dataframe,
                "BUY VALUE",
            ),
        }

    @classmethod
    def _validate_file(cls, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Selected path is not a file: {path}")

        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(cls.SUPPORTED_EXTENSIONS))
            raise ValueError(
                f"Unsupported file format '{path.suffix}'. "
                f"Supported formats: {supported}"
            )

    @staticmethod
    def _read_file(path: Path) -> pd.DataFrame:
        suffix = path.suffix.lower()

        try:
            if suffix == ".csv":
                return pd.read_csv(path)

            return pd.read_excel(path)

        except PermissionError as error:
            raise PermissionError(
                "Unable to open the file. Close it in Excel and try again."
            ) from error

        except Exception as error:
            raise ValueError(
                f"Unable to read '{path.name}': {error}"
            ) from error

    @staticmethod
    def _sum(dataframe: pd.DataFrame, column: str) -> float:
        if column not in dataframe.columns:
            return 0.0

        values = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        ).fillna(0.0)

        return float(values.sum())

    @staticmethod
    def _nunique(dataframe: pd.DataFrame, column: str) -> int:
        if column not in dataframe.columns:
            return 0

        return int(
            dataframe[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .nunique(dropna=True)
        )
