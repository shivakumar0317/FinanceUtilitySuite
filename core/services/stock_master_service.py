"""RMS v2.0.1 - Smart-cache stock master service."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable
from core.services.cache_service import CacheService
from core.services.sector_classifier import SectorClassifier
from core.services.yahoo_metadata_service import YahooMetadataService

@dataclass(slots=True)
class StockMasterResult:
    records: dict[str, dict[str, Any]]
    cache_hits: int
    live_fetches: int
    stale_fallbacks: int
    failures: dict[str, str]

class StockMasterService:
    def __init__(self, cache_service: CacheService | None = None, cache_ttl_days: int = 7, max_workers: int = 4):
        self.cache = cache_service or CacheService(ttl_days=cache_ttl_days)
        self.max_workers = max(1, min(int(max_workers), 8))

    def get_many(self, symbols, force_refresh: bool = False, progress_callback: Callable[[int, int, str], None] | None = None) -> StockMasterResult:
        symbols = sorted({YahooMetadataService.normalize_symbol(s) for s in symbols if str(s or "").strip()})
        records, stale, failures, misses = {}, {}, {}, []
        cache_hits = stale_fallbacks = 0
        for symbol in symbols:
            cached = None if force_refresh else self.cache.get(symbol)
            if cached is not None:
                records[symbol] = self._normalize(cached)
                cache_hits += 1
            else:
                misses.append(symbol)
                any_cache = self.cache.get_any(symbol)
                if any_cache is not None:
                    stale[symbol] = any_cache
        completed, total = cache_hits, len(symbols)
        fetched = {}
        if progress_callback:
            progress_callback(completed, total, "Loaded cache")
        if misses:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(YahooMetadataService.fetch, s): s for s in misses}
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        record = self._normalize(future.result().to_dict())
                        records[symbol] = fetched[symbol] = record
                    except Exception as error:
                        failures[symbol] = str(error)
                        if symbol in stale:
                            record = self._normalize(stale[symbol]); record["used_stale_cache"] = True
                            records[symbol] = record; stale_fallbacks += 1
                        else:
                            records[symbol] = self.default_record(symbol)
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, symbol)
        self.cache.set_many(fetched)
        return StockMasterResult(records, cache_hits, len(fetched), stale_fallbacks, failures)

    @staticmethod
    def default_record(symbol: str) -> dict[str, Any]:
        return {"symbol": symbol, "yahoo_symbol": "", "company_name": symbol, "sector": "Unclassified", "industry": "Unclassified", "market_cap": 0.0, "scrip_category": "Unclassified", "beta": 1.0, "current_price": 0.0, "currency": "INR", "exchange": "", "source": "Default", "metadata_status": "Unavailable"}

    @staticmethod
    def _normalize(record: dict[str, Any]) -> dict[str, Any]:
        result = dict(record)
        market_cap = StockMasterService._float(result.get("market_cap"))
        result["market_cap"] = market_cap
        result["scrip_category"] = SectorClassifier.classify_market_cap(market_cap)
        result["sector"] = SectorClassifier.normalize_sector(result.get("sector"))
        result["industry"] = SectorClassifier.normalize_industry(result.get("industry"))
        result["beta"] = StockMasterService._float(result.get("beta"), 1.0)
        result["current_price"] = StockMasterService._float(result.get("current_price"))
        result["company_name"] = str(result.get("company_name") or result.get("symbol") or "").strip()
        result["metadata_status"] = "Available" if market_cap > 0 or result["current_price"] > 0 else "Unavailable"
        return result

    @staticmethod
    def _float(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return float(default)
        return float(default) if number != number else number
