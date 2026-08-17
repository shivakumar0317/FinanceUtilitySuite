"""
Snapshot API Schemas

Pydantic models used by the
Enterprise RMS Snapshot APIs.

Author : Shiva Kumar
Version : 1.0.0
"""

from __future__ import annotations

from pydantic import BaseModel


# ---------------------------------------------------------
# Snapshot History Item
# ---------------------------------------------------------


class SnapshotHistoryItem(BaseModel):

    snapshot_id: str

    business_date: str

    timestamp: str

    filename: str

    records: int

    clients: int

    symbols: int

    portfolio_value: float

    total_exposure: float

    total_mtm: float

    risk_score: float

    health: str

    margin_utilization: float

    diversification_score: float

    top_client_concentration: float

    top_symbol_concentration: float

    source_file: str

    notes: str


# ---------------------------------------------------------
# Snapshot Comparison
# ---------------------------------------------------------


class SnapshotComparisonSchema(BaseModel):

    first_snapshot_id: str

    second_snapshot_id: str

    first_business_date: str

    second_business_date: str

    first_risk_score: float

    second_risk_score: float

    risk_score_change: float

    first_health: str

    second_health: str

    portfolio_value_change: float

    exposure_change: float

    mtm_change: float

    margin_utilization_change: float

    diversification_change: float

    client_change: int

    symbol_change: int

    record_change: int

    risk_trend: str