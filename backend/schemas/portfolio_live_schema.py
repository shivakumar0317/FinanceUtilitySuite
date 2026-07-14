from __future__ import annotations

from pydantic import BaseModel


class PortfolioLiveHolding(BaseModel):
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    invested_value: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float
    day_change: float
    day_change_percent: float


class PortfolioLiveSummary(BaseModel):
    invested_value: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float
    today_profit_loss: float
    total_holdings: int


class PortfolioLivePerformancePoint(BaseModel):
    date: str
    value: float


class PortfolioLiveDashboardResponse(BaseModel):
    summary: PortfolioLiveSummary
    holdings: list[PortfolioLiveHolding]
    performance: list[PortfolioLivePerformancePoint]
    top_holdings: list[PortfolioLiveHolding]
    top_gainers: list[PortfolioLiveHolding]
    top_losers: list[PortfolioLiveHolding]
