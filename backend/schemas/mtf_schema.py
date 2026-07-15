from __future__ import annotations

from pydantic import BaseModel


class MTFSummary(BaseModel):
    total_clients: int
    total_symbols: int
    total_buy_value: float
    total_net_value: float
    total_mtm: float
    total_margin: float
    average_margin_percent: float
    positive_mtm_clients: int
    negative_mtm_clients: int
    risk_level: str


class MarginDistributionItem(BaseModel):
    range: str
    clients: int
    margin_value: float


class SymbolExposureItem(BaseModel):
    symbol: str
    buy_value: float
    net_value: float
    mtm: float
    margin: float
    clients: int


class TopMarginClientItem(BaseModel):
    account_id: str
    margin: float
    buy_value: float
    net_value: float
    mtm: float
    symbols: int


class TopMarginSymbolItem(BaseModel):
    symbol: str
    margin: float
    buy_value: float
    net_value: float
    mtm: float
    clients: int


class TopMTMItem(BaseModel):
    account_id: str
    symbol: str
    mtm: float
    buy_value: float
    margin: float


class ClientRiskItem(BaseModel):
    account_id: str
    buy_value: float
    net_value: float
    mtm: float
    margin: float
    margin_percent: float
    mtm_percent: float
    symbols: int
    risk_score: float
    risk_level: str


class MTFDashboardResponse(BaseModel):
    summary: MTFSummary
    margin_distribution: list[MarginDistributionItem]
    symbol_exposure: list[SymbolExposureItem]
    top_margin_clients: list[TopMarginClientItem]
    top_margin_symbols: list[TopMarginSymbolItem]
    top_mtm_gainers: list[TopMTMItem]
    top_mtm_losers: list[TopMTMItem]
    client_risk: list[ClientRiskItem]
