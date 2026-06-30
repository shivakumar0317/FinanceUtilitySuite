"""
Yahoo Finance Service
Author: Finance Utility Suite

This module fetches stock information from Yahoo Finance.
"""

import yfinance as yf
from core.logger import AppLogger


class YahooService:

    def __init__(self):

        self.logger = AppLogger()

    # -----------------------------------
    # Fetch Stock Information
    # -----------------------------------

    def get_stock_info(self, symbol):

        symbol = str(symbol).strip().upper()

        exchanges = [
            symbol + ".NS",
            symbol + ".BO"
        ]

        for ticker_name in exchanges:

            try:

                ticker = yf.Ticker(ticker_name)

                info = ticker.info

                if not info:
                    continue

                beta = info.get("beta")

                if beta is None:
                    continue

                self.logger.info(f"{ticker_name} fetched successfully")

                return {

                    "Symbol": symbol,
                    "Exchange": ticker_name,

                    "Company": info.get("longName"),

                    "CMP": info.get("currentPrice"),

                    "Beta": info.get("beta"),

                    "Market Cap": info.get("marketCap"),

                    "PE": info.get("trailingPE"),

                    "EPS": info.get("trailingEps"),

                    "Sector": info.get("sector"),

                    "Industry": info.get("industry"),

                    "Dividend Yield": info.get("dividendYield"),

                    "52 Week High": info.get("fiftyTwoWeekHigh"),

                    "52 Week Low": info.get("fiftyTwoWeekLow")

                }

            except Exception as e:

                self.logger.error(f"{ticker_name} : {e}")

        return None