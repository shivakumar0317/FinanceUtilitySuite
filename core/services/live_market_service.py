"""
Finance Utility Suite
Live Market Service

Version: 1.10
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf


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

    @classmethod
    def get_top_movers(cls):
        gainers = [
            ("RELIANCE", 2.35),
            ("TCS", 1.92),
            ("HDFCBANK", 1.64),
            ("ICICIBANK", 1.42),
            ("SBIN", 1.15),
        ]

        losers = [
            ("INFY", -1.25),
            ("WIPRO", -0.90),
            ("BAJAJFIN", -0.76),
            ("LT", -0.64),
            ("TITAN", -0.55),
        ]

        return gainers, losers

    @classmethod
    def get_watchlist_prices(
        cls,
        symbols: list[str],
    ) -> pd.DataFrame:
        rows = []

        for symbol in symbols:
            try:
                ticker = yf.Ticker(f"{symbol}.NS")
                info = ticker.fast_info

                price = float(info.get("lastPrice", 0))
                previous = float(
                    info.get("previousClose", price)
                )

                change = price - previous
                change_pct = (
                    (change / previous) * 100
                    if previous
                    else 0
                )

                rows.append(
                    {
                        "Symbol": symbol,
                        "Price": price,
                        "Change %": change_pct,
                    }
                )

            except Exception:
                rows.append(
                    {
                        "Symbol": symbol,
                        "Price": 0,
                        "Change %": 0,
                    }
                )

        return pd.DataFrame(rows)