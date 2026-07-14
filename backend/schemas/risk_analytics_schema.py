from __future__ import annotations

from pydantic import BaseModel


class RiskMetricSummary(BaseModel):
    portfolio_beta: float
    volatility: float
    alpha: float
    sharpe_ratio: float
    max_drawdown: float
    concentration_risk: float
    diversification_score: float
    risk_level: str
    benchmark_symbol: str
    analysis_period: str


class RiskPerformancePoint(BaseModel):
    date: str
    portfolio: float
    benchmark: float


class DrawdownPoint(BaseModel):
    date: str
    drawdown: float


class SectorExposureItem(BaseModel):
    sector: str
    value: float
    weight_percent: float


class TopRiskHoldingItem(BaseModel):
    symbol: str
    current_value: float
    portfolio_weight: float
    beta: float | None
    annualized_volatility: float | None
    risk_contribution: float
    sector: str


class RiskAnalyticsDashboardResponse(BaseModel):
    summary: RiskMetricSummary
    performance: list[RiskPerformancePoint]
    drawdown: list[DrawdownPoint]
    sector_exposure: list[SectorExposureItem]
    top_risk_holdings: list[TopRiskHoldingItem]
