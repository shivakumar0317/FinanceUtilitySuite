from core.stock_service import StockService

service = StockService()

df = service.read_file("data/Funded Stocks.xlsx")  # Change filename if needed

service.validate_dataframe(df)

symbols = service.prepare_symbols(df)

print(f"Found {len(symbols)} symbols")

report = service.analyze_symbols(symbols[:5])  # First 5 stocks

print(report)
