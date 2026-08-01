from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass(slots=True)
class RiskItem:
    name: str
    exposure: float
    mtm: float
    concentration_percent: float
    score: float
    level: str
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(slots=True)
class RiskAlert:
    level: str
    title: str
    message: str
    recommendation: str
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(slots=True)
class RiskSummary:
    overall_score: float
    health: str
    health_reason: str
    records: int
    clients: int
    symbols: int
    portfolio_value: float
    total_exposure: float
    total_mtm: float
    total_var: float
    total_margin: float
    mtm_loss_percent: float
    margin_utilization_percent: float
    top_client_concentration_percent: float
    top_symbol_concentration_percent: float
    exposure_score: float
    mtm_score: float
    margin_score: float
    client_concentration_score: float
    symbol_concentration_score: float
    diversification_score: float
    calculated_score: float | None = None
    display_score: float | None = None
    top_clients: list[RiskItem] = field(default_factory=list)
    top_symbols: list[RiskItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    alerts: list[RiskAlert] = field(default_factory=list)
    snapshot_id: str = ''
    last_refresh: str = ''
    engine_status: str = 'Ready'
    def __post_init__(self):
        if self.calculated_score is None: self.calculated_score=float(self.overall_score)
        if self.display_score is None: self.display_score=float(self.calculated_score)
    def to_dict(self) -> dict[str, Any]:
        payload=asdict(self)
        payload['top_clients']=[x.to_dict() for x in self.top_clients]
        payload['top_symbols']=[x.to_dict() for x in self.top_symbols]
        payload['alerts']=[x.to_dict() for x in self.alerts]
        return payload
