from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class SnapshotMetadata:
    snapshot_id: str
    timestamp: str
    filename: str
    relative_path: str
    records: int
    clients: int
    symbols: int
    portfolio_value: float
    total_exposure: float
    total_mtm: float
    source_file: str = ""
    notes: str = ""

    @property
    def timestamp_value(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)

    @property
    def path(self) -> Path:
        return Path(self.relative_path)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SnapshotMetadata":
        return cls(
            snapshot_id=str(value["snapshot_id"]), timestamp=str(value["timestamp"]),
            filename=str(value["filename"]), relative_path=str(value["relative_path"]),
            records=int(value.get("records",0)), clients=int(value.get("clients",0)),
            symbols=int(value.get("symbols",0)), portfolio_value=float(value.get("portfolio_value",0.0)),
            total_exposure=float(value.get("total_exposure",0.0)), total_mtm=float(value.get("total_mtm",0.0)),
            source_file=str(value.get("source_file","")), notes=str(value.get("notes","")),
        )
