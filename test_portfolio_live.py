import pandas as pd

from core.services.portfolio_live_service import (
    PortfolioLiveService,
)

df = pd.DataFrame(
    {
        "SYMBOL": ["RELIANCE", "TCS"],
        "QTY": [10, 20],
        "AVG_PRICE": [2500, 3500],
    }
)

df = PortfolioLiveService.refresh_prices(df)

print(df)