from core.stock_service import StockService
from core.excel_service import ExcelService

stock_service = StockService()

excel_service = ExcelService()

# Read your Excel file
df = stock_service.read_file("data/Funded Stocks.xlsx")  # Change filename if needed

stock_service.validate_dataframe(df)

symbols = stock_service.prepare_symbols(df)

# Analyze first 10 stocks for testing
report = stock_service.analyze_symbols(symbols[:10])

# Export to Excel
file = excel_service.export(report)

print(file)
