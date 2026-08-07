"""Enterprise Snapshot Manager service."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from core.models.snapshot import SnapshotMetadata
from core.snapshots.snapshot_repository import SnapshotRepository


class SnapshotManagerService:
    """Application-facing operations for historical RMS snapshots."""

    def __init__(
        self,
        repository: SnapshotRepository | None = None,
        root_dir: str | Path = "data/snapshots",
    ) -> None:
        self.repository = repository or SnapshotRepository(root_dir)

    def list_metadata(self, query: str = "") -> list[SnapshotMetadata]:
        snapshots = self.repository.list_snapshots()
        query = str(query).strip().lower()
        if not query:
            return snapshots

        def matches(item: SnapshotMetadata) -> bool:
            status, _level = self.health_status(item)
            formatted_date = self.format_timestamp(item.timestamp)
            haystack = " ".join(
                [
                    item.snapshot_id,
                    item.timestamp,
                    formatted_date,
                    item.source_file,
                    item.notes,
                    status,
                    str(item.records),
                    str(item.clients),
                    str(item.symbols),
                ]
            ).lower()
            return query in haystack

        return [item for item in snapshots if matches(item)]

    def get_metadata(self, snapshot_id: str) -> SnapshotMetadata | None:
        return self.repository.get_metadata(str(snapshot_id).strip())

    def load_snapshot(self, snapshot_id: str) -> pd.DataFrame:
        snapshot_id = str(snapshot_id).strip()
        if not snapshot_id:
            raise ValueError("Snapshot ID is required.")
        return self.repository.load(snapshot_id)

    def export_to_excel(self, snapshot_id: str, output_path: str | Path) -> Path:
        dataframe = self.load_snapshot(snapshot_id)
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_excel(target, index=False)
        return target

    def delete_snapshot(self, snapshot_id: str) -> bool:
        return self.repository.delete(str(snapshot_id).strip())

    def summary(self, snapshots: list[SnapshotMetadata] | None = None) -> dict[str, float | int]:
        items = snapshots if snapshots is not None else self.list_metadata()
        latest = items[0] if items else None
        return {
            "snapshots": len(items),
            "records": latest.records if latest else 0,
            "clients": latest.clients if latest else 0,
            "symbols": latest.symbols if latest else 0,
            "portfolio_value": latest.portfolio_value if latest else 0.0,
            "exposure": latest.total_exposure if latest else 0.0,
            "mtm": latest.total_mtm if latest else 0.0,
        }

    @staticmethod
    def health_status(metadata: SnapshotMetadata | None) -> tuple[str, str]:
        """Temporary health rules until Sprint 4 Risk Engine replaces them."""
        if metadata is None:
            return "No Data", "neutral"

        exposure = abs(float(metadata.total_exposure or 0.0))
        mtm = float(metadata.total_mtm or 0.0)
        if exposure <= 0:
            return "Healthy", "healthy"

        loss_ratio = abs(min(mtm, 0.0)) / exposure
        if loss_ratio >= 0.08:
            return "Critical", "critical"
        if loss_ratio >= 0.03:
            return "Warning", "warning"
        return "Healthy", "healthy"

    @staticmethod
    def format_timestamp(value: str) -> str:
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return str(value)
        return parsed.strftime("%d-%b-%Y %I:%M:%S %p")

    @staticmethod
    def format_indian_compact(value: float | int) -> str:
        """Format large values using Indian units while retaining sensible precision."""
        number = float(value or 0.0)
        sign = "-" if number < 0 else ""
        absolute = abs(number)
        if absolute >= 10_000_000:
            return f"{sign}₹{absolute / 10_000_000:.2f} Cr"
        if absolute >= 100_000:
            return f"{sign}₹{absolute / 100_000:.2f} L"
        if absolute >= 1_000:
            return f"{sign}₹{absolute / 1_000:.2f} K"
        return f"{sign}₹{absolute:,.2f}"

    @staticmethod
    def format_money(value: float | int) -> str:
        number = float(value or 0.0)
        sign = "-" if number < 0 else ""
        return f"{sign}₹{abs(number):,.2f}"

    def latest_snapshot(self) -> SnapshotMetadata | None:
        snapshots = self.list_metadata()
        if not snapshots:
            return None

        snapshots.sort(
        key=lambda x: x.business_date,
        reverse=True,
        )
        return snapshots[0]
