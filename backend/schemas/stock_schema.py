from __future__ import annotations

from pydantic import BaseModel


class StockHistoryPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockDetails(BaseModel):
    symbol: str
    resolved_symbol: str
    company_name: str
    sector: str
    industry: str
    exchange: str
    currency: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    market_cap: float | None
    pe_ratio: float | None
    price_to_book: float | None
    dividend_yield: float | None
    beta: float | None
    roe: float | None
    debt_to_equity: float | None
    profit_margin: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None


class StockAnalysis(BaseModel):
    investment_score: int
    risk_score: int
    risk_level: str
    recommendation: str
    star_rating: str
    reasons: list[str]


class StockAnalyzerResponse(BaseModel):
    details: StockDetails
    analysis: StockAnalysis
    history: list[StockHistoryPoint]
