from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class SnapshotMetadata:
    snapshot_id: str
    business_date: str
    timestamp: str
    filename: str
    relative_path: str
    records: int
    clients: int
    symbols: int
    portfolio_value: float
    total_exposure: float
    total_mtm: float

    risk_score: float = 0.0
    health: str = "Unknown"

    margin_utilization: float = 0.0
    diversification_score: float = 0.0

    top_client_concentration: float = 0.0
    top_symbol_concentration: float = 0.0

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
            snapshot_id=str(value["snapshot_id"]), business_date=str(value.get("business_date",str(value["timestamp"])[:10],)), timestamp=str(value["timestamp"]),
            filename=str(value["filename"]), relative_path=str(value["relative_path"]),
            records=int(value.get("records",0)), clients=int(value.get("clients",0)),
            symbols=int(value.get("symbols",0)), portfolio_value=float(value.get("portfolio_value",0.0)),
            total_exposure=float(value.get("total_exposure",0.0)), total_mtm=float(value.get("total_mtm",0.0)),
            risk_score=float(value.get("risk_score",0.0)), health=str(value.get("health","Unknown")),
            margin_utilization=float(value.get("margin_utilization",0.0)),
            diversification_score=float(value.get("diversification_score",0.0)),
            top_client_concentration=float(value.get("top_client_concentration",0.0)),
            top_symbol_concentration=float(value.get("top_symbol_concentration",0.0)),
            source_file=str(value.get("source_file","")), notes=str(value.get("notes","")),
        )
