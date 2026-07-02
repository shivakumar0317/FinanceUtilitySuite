from core.yahoo_service import YahooService

service = YahooService()

stock = service.get_stock_info("RELIANCE")

print(stock)
