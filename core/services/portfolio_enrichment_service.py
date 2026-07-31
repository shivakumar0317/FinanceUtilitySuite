"""RMS v2.0.1 - Portfolio enrichment engine."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import pandas as pd
from core.services.stock_master_service import StockMasterService
from core.state.application_state import ApplicationState

@dataclass(slots=True)
class EnrichmentResult:
    dataframe: pd.DataFrame
    symbols: int
    enriched_symbols: int
    cache_hits: int
    live_fetches: int
    stale_fallbacks: int
    failures: dict[str, str]

class PortfolioEnrichmentService:
    COLUMN_MAP = {
        "company_name": "Company Name", "sector": "Sector", "industry": "Industry",
        "market_cap": "Market Cap", "scrip_category": "Scrip Category", "beta": "Beta",
        "current_price": "Current Price", "currency": "Currency", "exchange": "Exchange",
        "yahoo_symbol": "Yahoo Symbol", "source": "Metadata Source", "metadata_status": "Metadata Status",
    }

    def __init__(self, stock_master_service: StockMasterService | None = None):
        self.stock_master = stock_master_service or StockMasterService()

    def enrich(self, dataframe: pd.DataFrame | None = None, force_refresh: bool = False,
               source_file: str | None = None,
               progress_callback: Callable[[int, int, str], None] | None = None) -> EnrichmentResult:
        portfolio = dataframe.copy() if dataframe is not None else ApplicationState.get_master_portfolio()
        if portfolio is None or portfolio.empty:
            raise ValueError("No master portfolio is available for enrichment.")
        if "Symbol" not in portfolio.columns:
            raise ValueError("Portfolio enrichment requires a Symbol column.")
        portfolio["Symbol"] = portfolio["Symbol"].fillna("").astype(str).str.strip().str.upper().str.removesuffix(".NS").str.removesuffix(".BO")
        symbols = [s for s in portfolio["Symbol"].unique().tolist() if s]
        result = self.stock_master.get_many(symbols, force_refresh, progress_callback)
        rows = []
        for symbol, record in result.records.items():
            row = {"Symbol": symbol}
            for source, target in self.COLUMN_MAP.items():
                row[target] = record.get(source)
            rows.append(row)
        metadata = pd.DataFrame(rows, columns=["Symbol", *self.COLUMN_MAP.values()])
        portfolio = portfolio.drop(columns=[c for c in self.COLUMN_MAP.values() if c in portfolio.columns], errors="ignore")
        enriched = portfolio.merge(metadata, on="Symbol", how="left", validate="many_to_one")
        enriched = self._recalculate(enriched)
        ApplicationState.set_master_portfolio(enriched, source_file=source_file or ApplicationState.get_source_file())
        available = int(metadata["Metadata Status"].eq("Available").sum()) if not metadata.empty else 0
        return EnrichmentResult(enriched.copy(), len(symbols), available, result.cache_hits, result.live_fetches, result.stale_fallbacks, result.failures)

    @classmethod
    def enrich_application_state(cls, force_refresh: bool = False, progress_callback=None) -> EnrichmentResult:
        return cls().enrich(force_refresh=force_refresh, progress_callback=progress_callback)

    @staticmethod
    def _recalculate(df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        for column in ("NetQty", "BUY VALUE", "NetValue", "MarkToMarket", "Market Cap", "Beta", "Current Price"):
            if column in result.columns:
                result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0.0)
        index = result.index
        qty = result.get("NetQty", pd.Series(0.0, index=index)).abs()
        price = result.get("Current Price", pd.Series(0.0, index=index))
        fallback = result.get("NetValue", pd.Series(0.0, index=index)).abs()
        result["Current Value"] = (qty * price).where(price.gt(0), fallback)
        result["Profit/Loss"] = result.get("MarkToMarket", pd.Series(0.0, index=index))
        buy = result.get("BUY VALUE", pd.Series(0.0, index=index)).abs()
        result["Return %"] = result["Profit/Loss"].div(buy.where(buy.ne(0))).mul(100).fillna(0.0)
        total = float(result["Current Value"].sum())
        result["Allocation %"] = result["Current Value"].div(total).mul(100) if total > 0 else 0.0
        beta = result.get("Beta", pd.Series(1.0, index=index)).replace(0, 1.0)
        result["Risk %"] = result["Allocation %"] * beta
        return result
