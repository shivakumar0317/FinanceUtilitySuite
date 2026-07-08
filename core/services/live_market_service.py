"""
Finance Utility Suite
Live Market Service

Version: 1.10
"""

from __future__ import annotations

import yfinance as yf
import pandas as pd


class LiveMarketService:

    INDICES = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANKNIFTY": "^NSEBANK",
        "INDIA VIX": "^INDIAVIX",
    }

    @classmethod
    def get_indices(cls) -> pd.DataFrame:
        rows = []

        for name, ticker_symbol in cls.INDICES.items():
            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.fast_info

                current = info.get("lastPrice", 0)
                previous = info.get("previousClose", current)

                change = current - previous
                pct = (
                    (change / previous) * 100
                    if previous
                    else 0
                )

                rows.append(
                    {
                        "Index": name,
                        "Price": current,
                        "Change": change,
                        "Change %": pct,
                    }
                )

            except Exception:
                rows.append(
                    {
                        "Index": name,
                        "Price": 0,
                        "Change": 0,
                        "Change %": 0,
                    }
                )

        return pd.DataFrame(rows)