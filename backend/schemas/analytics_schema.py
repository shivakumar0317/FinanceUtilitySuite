from __future__ import annotations

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_investment: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float
    total_holdings: int


class AllocationItem(BaseModel):
    name: str
    value: float


class ProfitLossItem(BaseModel):
    symbol: str
    profit_loss: float
    profit_loss_percent: float


class TopHoldingItem(BaseModel):
    symbol: str
    value: float


class PerformancePoint(BaseModel):
    date: str
    value: float


class AnalyticsDashboardResponse(BaseModel):
    summary: AnalyticsSummary
    allocation: list[AllocationItem]
    profit_loss: list[ProfitLossItem]
    top_holdings: list[TopHoldingItem]
    performance: list[PerformancePoint]
