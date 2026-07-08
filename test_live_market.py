from core.services.live_market_service import LiveMarketService

df = LiveMarketService.get_indices()

print(df)