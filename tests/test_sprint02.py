from core.services.cache_service import CacheService
from core.services.sector_classifier import SectorClassifier
from core.services.yahoo_metadata_service import YahooMetadataService

def main():
    assert SectorClassifier.classify_market_cap(25000, "crore") == "Large Cap"
    assert SectorClassifier.classify_market_cap(10000, "crore") == "Mid Cap"
    assert SectorClassifier.classify_market_cap(5000, "crore") == "Small Cap"
    assert YahooMetadataService.normalize_symbol(" reliance.ns ") == "RELIANCE"
    cache = CacheService("tests/test_stock_master_cache.json", 7)
    cache.clear(); cache.set("RELIANCE", {"company_name": "Reliance"})
    assert cache.get("RELIANCE") is not None
    cache.clear()
    print("RMS Sprint 2 local tests passed successfully.")

if __name__ == "__main__":
    main()
