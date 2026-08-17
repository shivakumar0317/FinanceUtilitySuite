"""
Dashboard API Schemas

Pydantic models used by the
Enterprise Dashboard API.

Author : Shiva Kumar
Version : 2.0.0
"""

from __future__ import annotations

from pydantic import BaseModel


# ---------------------------------------------------------
# Executive Summary
# ---------------------------------------------------------

class ExecutiveSummarySchema(BaseModel):

    risk_score: float

    health: str

    total_exposure: float

    total_mtm: float

    margin_utilization: float

    diversification: float


# ---------------------------------------------------------
# Snapshot
# ---------------------------------------------------------

class SnapshotSchema(BaseModel):

    snapshot_id: str

    business_date: str

    records: int

    clients: int

    symbols: int


# ---------------------------------------------------------
# Risk Item
# ---------------------------------------------------------

class RiskItemSchema(BaseModel):

    name: str

    exposure: float

    mtm: float

    concentration_percent: float

    score: float

    level: str


# ---------------------------------------------------------
# Alert
# ---------------------------------------------------------

class AlertSchema(BaseModel):

    level: str

    title: str

    message: str

    recommendation: str


# ---------------------------------------------------------
# Dashboard Response
# ---------------------------------------------------------

class DashboardSchema(BaseModel):

    summary: ExecutiveSummarySchema

    snapshot: SnapshotSchema

    top_clients: list[RiskItemSchema]

    top_symbols: list[RiskItemSchema]

    alerts: list[AlertSchema]