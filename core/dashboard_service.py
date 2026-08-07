from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from core.models.risk_summary import RiskSummary
from core.services.risk_engine import RiskEngine
from core.models.snapshot import SnapshotMetadata
from core.services.snapshot_manager_service import SnapshotManagerService

@dataclass(slots=True)
class DashboardData:
    summary: RiskSummary | None
    snapshot: SnapshotMetadata | None
    available: bool
    message: str
    def to_dict(self) -> dict[str, Any]:
        return {
        "summary": self.summary.to_dict() if self.summary else None,
        "snapshot": self.snapshot.to_dict() if self.snapshot else None,
        "available": self.available,
        "message": self.message,
    }
class DashboardService:
    def get_dashboard_data(self) -> DashboardData:
        try:
            summary = RiskEngine.analyze_current_portfolio()
            snapshot = SnapshotManagerService().latest_snapshot()

        except ValueError as exc:
            return DashboardData(
            summary=None,
            snapshot=None,
            available=False,
            message=str(exc),
        )

        except Exception as exc:
            return DashboardData(
            summary=None,
            snapshot=None,
            available=False,
            message=f"Unable to calculate portfolio risk: {exc}",
        )

        return DashboardData(
            summary=summary,
            snapshot=snapshot,
            available=True,
            message="Enterprise risk dashboard loaded successfully.",
        )
    
    def get_statistics(self):
        data=self.get_dashboard_data()
        if not data.available or data.summary is None: return {'stocks':0,'reports':0,'avg_beta':'0.00','high_risk':0}
        s=data.summary
        return {'stocks':s.symbols,'reports':0,'avg_beta':'0.00','high_risk':sum(1 for x in s.top_symbols if x.level=='Critical')}
