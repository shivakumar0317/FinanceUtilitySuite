from modules.stock_analyzer import StockAnalyzer

analyzer = StockAnalyzer()

stock = analyzer.get_stock_data("RELIANCE")

print(stock)
