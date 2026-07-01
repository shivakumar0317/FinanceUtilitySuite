from core.services.market_data_service import MarketDataService

price = MarketDataService.get_current_price("INFY")

print(price)

info = MarketDataService.get_company_info("INFY")

print(info)