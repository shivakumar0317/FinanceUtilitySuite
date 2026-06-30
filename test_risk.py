from core.yahoo_service import YahooService
from core.risk_service import RiskService

stock = YahooService().get_stock_info("RELIANCE")

risk = RiskService()

score = risk.investment_score(stock)

print(stock["Company"])
print(stock["Beta"])
print(risk.get_beta_risk(stock["Beta"]))
print(score)
print(risk.star_rating(score))