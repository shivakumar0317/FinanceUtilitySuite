"""
Stock Service
Finance Utility Suite

Reads stock files and prepares a clean symbol list.
"""

from pathlib import Path

import pandas as pd

from core.logger import AppLogger
from core.yahoo_service import YahooService
from core.risk_service import RiskService


class StockService:

    def __init__(self):

        self.logger = AppLogger()

        self.yahoo = YahooService()

        self.risk = RiskService()

    # --------------------------------------------------
    # Read CSV / Excel
    # --------------------------------------------------

    def read_file(self, filename):

        filename = Path(filename)

        self.logger.info(f"Reading file : {filename.name}")

        if filename.suffix.lower() == ".csv":

            df = pd.read_csv(filename)

        elif filename.suffix.lower() == ".xlsx":

            df = pd.read_excel(filename)

        else:

            raise Exception("Unsupported file format.")

        return df

    # --------------------------------------------------
    # Validate SYMBOL Column
    # --------------------------------------------------

    def validate_dataframe(self, dataframe):

        if "SYMBOL" not in dataframe.columns:

            raise Exception("SYMBOL column not found.")

        self.logger.info("SYMBOL column verified.")

        return True

    # --------------------------------------------------
    # Prepare Symbols
    # --------------------------------------------------

    def prepare_symbols(self, dataframe):

        symbols = []

        for symbol in dataframe["SYMBOL"]:

            if pd.isna(symbol):
                continue

            symbol = str(symbol).strip().upper()

            if symbol == "":
                continue

            symbols.append(symbol)

        # Remove duplicates while keeping order

        unique_symbols = list(dict.fromkeys(symbols))

        self.logger.info(
            f"{len(unique_symbols)} unique symbols prepared."
        )

        return unique_symbols
    
        # --------------------------------------------------
    # Analyze Symbols
    # --------------------------------------------------

    def analyze_symbols(self, symbols, progress_callback=None):

        results = []

        total = len(symbols)

        self.logger.info(f"Analyzing {total} stocks.")

        for index, symbol in enumerate(symbols, start=1):

         if progress_callback:

            progress = index / len(symbols)

            progress_callback(index, len(symbols), symbol, progress)

            self.logger.info(f"{index}/{total} : {symbol}")

            stock = self.yahoo.get_stock_info(symbol)

            if stock is None:

                self.logger.warning(f"{symbol} skipped.")

                continue

            beta = stock.get("Beta")

            stock["Risk"] = self.risk.get_beta_risk(beta)

            score = self.risk.investment_score(stock)

            stock["Score"] = score

            stock["Rating"] = self.risk.star_rating(score)

            results.append(stock)

        dataframe = pd.DataFrame(results)

        if not dataframe.empty:

            if "CMP" in dataframe.columns:
                dataframe["CMP"] = dataframe["CMP"].round(2)

            if "Beta" in dataframe.columns:
                dataframe["Beta"] = dataframe["Beta"].round(2)

            if "PE" in dataframe.columns:
                dataframe["PE"] = dataframe["PE"].round(2)

        return dataframe