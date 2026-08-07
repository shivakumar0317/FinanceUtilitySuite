"""
Finance Utility Suite
Enterprise RMS

Module:
    snapshot_service.py

Description:
    Creates and manages portfolio snapshots.
"""

from __future__ import annotations

from datetime import datetime, date
import re
from pathlib import Path
from uuid import uuid4

import pandas as pd

from core.models.snapshot import SnapshotMetadata
from core.services.enterprise_risk_service import EnterpriseRiskService
from core.snapshots.snapshot_repository import SnapshotRepository


class SnapshotService:
    """
    Snapshot management service.
    """

    def __init__(
        self,
        repository: SnapshotRepository | str | Path = "data/snapshots",
    ) -> None:
        """
        Initialize SnapshotService.

        Parameters
        ----------
        repository
            Either:
            - an existing SnapshotRepository (used by tests), or
            - a snapshot root path (used by the application).
            """

        if isinstance(repository, SnapshotRepository):
            self.repository = repository
        else:
            self.repository = SnapshotRepository(repository)

    @staticmethod
    def _extract_business_date(source_file: str, created: datetime) -> str:
        """
        Extract business date from the source file.

        Priority
        --------
        1. Filename (MTF_03082026.xlsx)
        2. Snapshot creation date
        """

        if source_file:

            filename = Path(source_file).name

        match = re.search(r"(\d{2})(\d{2})(\d{4})", filename)

        if match:

            try:

                return datetime.strptime(
                    match.group(0),
                    "%d%m%Y",
                ).date().isoformat()

            except ValueError:
                pass

        return created.date().isoformat() 

    def create_snapshot(
        self,
        dataframe: pd.DataFrame,
        *,
        source_file: str = "",
        notes: str = "",
        timestamp: datetime | None = None,
    ) -> SnapshotMetadata:
        """
        Create and save a snapshot.

        Parameters
        ----------
        dataframe
            Portfolio dataframe.

        source_file
            Original Excel file.

        notes
            Optional notes.

        timestamp
            Snapshot timestamp.

        Returns
        -------
        SnapshotMetadata
        """

        if dataframe is None:
            raise ValueError("DataFrame is None.")

        if dataframe.empty:
            raise ValueError("DataFrame is empty.")

        created = timestamp or datetime.now()

        business_date = self._extract_business_date(
        source_file,
        created,
        )

        snapshot_id = (
            created.strftime("%Y%m%d_%H%M%S")
            + "_"
            + uuid4().hex[:6]
        )

        filename = f"{snapshot_id}.parquet"

        relative_path = str(
            Path(
                created.strftime("%Y-%m"),
                filename,
            )
        )

        summary = EnterpriseRiskService.analyze(
            dataframe,
        )

        metadata = SnapshotMetadata(
            snapshot_id=snapshot_id,

            business_date=business_date,

            timestamp=created.isoformat(timespec="seconds"),
            filename=filename,
            relative_path=relative_path,

            records=summary.records,
            clients=summary.clients,
            symbols=summary.symbols,

            portfolio_value=summary.portfolio_value,
            total_exposure=summary.total_exposure,
            total_mtm=summary.total_mtm,

            risk_score=summary.overall_score,
            health=summary.health,

            margin_utilization=summary.margin_utilization_percent,
            diversification_score=summary.diversification_score,

            top_client_concentration=(
                summary.top_client_concentration_percent
            ),

            top_symbol_concentration=(
                summary.top_symbol_concentration_percent
            ),

            source_file=str(source_file),
            notes=notes,
        )

        self.repository.save(
            dataframe,
            metadata,
        )

        return metadata

    def load_snapshot(
        self,
        snapshot_id: str,
    ) -> pd.DataFrame:
        """
        Load snapshot dataframe.
        """
        return self.repository.load(snapshot_id)

    def compare_snapshots(
        self,
        first_snapshot_id: str,
        second_snapshot_id: str,
    ) -> dict:
        """
        Compare two snapshots.

        Returns
        -------
        dict
        Summary of portfolio changes.
        """

        first = self.repository.get_metadata(first_snapshot_id)
        second = self.repository.get_metadata(second_snapshot_id)

        if first is None:
            raise FileNotFoundError(first_snapshot_id)

        if second is None:
            raise FileNotFoundError(second_snapshot_id)

        return {
            "portfolio_value_change":
            second.portfolio_value
            - first.portfolio_value,

        "exposure_change":
            second.total_exposure
            - first.total_exposure,

        "mtm_change":
            second.total_mtm
            - first.total_mtm,

        "client_change":
            second.clients
            - first.clients,

        "symbol_change":
            second.symbols
            - first.symbols,

        "record_change":
            second.records
            - first.records,
    }

    def list_snapshots(
        self,
    ) -> list[SnapshotMetadata]:
        """
        Return all snapshots.
        """
        return self.repository.list_snapshots()

    def latest_snapshot(
        self,
    ) -> SnapshotMetadata | None:
        """
        Return latest snapshot.
        """
        return self.repository.latest()

    def delete_snapshot(
        self,
        snapshot_id: str,
    ) -> bool:
        """
        Delete a snapshot.
        """
        return self.repository.delete(snapshot_id)