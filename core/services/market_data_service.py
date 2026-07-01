"""
Finance Utility Suite
Market Data Service
"""

from __future__ import annotations

import time

import yfinance as yf


class MarketDataService:
    """
    Fetches market prices using Yahoo Finance with simple cache.
    """

    CACHE_TIMEOUT = 300  # 5 minutes

    _price_cache = {}

    @classmethod
    def get_current_price(cls, symbol: str) -> float:

        symbol = symbol.strip().upper()

        if not symbol:
            return 0.0

        # Cache check
        if symbol in cls._price_cache:
            price, timestamp = cls._price_cache[symbol]

            if time.time() - timestamp < cls.CACHE_TIMEOUT:
                return price

        # Try NSE, then BSE, then raw symbol
        ticker_symbols = [
            f"{symbol}.NS",
            f"{symbol}.BO",
            symbol
        ]

        for ticker_symbol in ticker_symbols:

            try:
                ticker = yf.Ticker(ticker_symbol)

                history = ticker.history(period="5d")

                if not history.empty:
                    price = float(history["Close"].dropna().iloc[-1])

                    cls._price_cache[symbol] = (
                        price,
                        time.time()
                    )

                    return price

            except Exception:
                continue

        return 0.0

    @classmethod
    def clear_cache(cls):

        cls._price_cache.clear()